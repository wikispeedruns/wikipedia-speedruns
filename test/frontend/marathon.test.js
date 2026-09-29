import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { resolveCheckpointTitles, validateCheckpoints, creditCheckpoint } from "../../frontend/static/js/modules/game/marathon/checkpoints.js";
import { MarathonBuilder } from "../../frontend/static/js/modules/prompts/marathon-submit.js";

const originalFetch = globalThis.fetch;
beforeEach(() => { globalThis.fetch = async () => { throw new Error("Unexpected request"); }; });
afterEach(() => { globalThis.fetch = originalFetch; });
const reply = query => ({ok: true, json: async () => ({query})});
const game = (title, resolved, reserve = []) => ({
    activeCheckpoints: [title], resolvedCheckpointTitles: resolved, checkpoints: reserve,
    visitedCheckpoints: [], clicksRemaining: 0, clicksPerCheckpoint: 2
});

test("reported redirects earn credit once, including the final checkpoint", async () => {
    globalThis.fetch = async () => reply({
        normalized: [{from: "Duffer_brothers", to: "Duffer brothers"}],
        redirects: [
            {from: "Duffer brothers", to: "Duffer Brothers"},
            {from: "Duffer Brothers", to: "The Duffer Brothers"},
            {from: "Rainbow flag (LGBT)", to: "Rainbow flag (LGBTQ)"}
        ],
        pages: [{title: "The Duffer Brothers", ns: 0}, {title: "Rainbow flag (LGBTQ)", ns: 0}]
    });
    const resolved = await resolveCheckpointTitles(["Duffer_brothers", "Rainbow flag (LGBT)"]);
    for (const [stored, canonical] of Object.entries(resolved)) {
        const state = game(stored, resolved);
        assert.equal(creditCheckpoint(state, "Unrelated"), false);
        assert.equal(creditCheckpoint(state, canonical.replaceAll(" ", "_").toLowerCase()), true);
        assert.equal(state.clicksRemaining, 3);
        assert.equal(state.visitedCheckpoints.length, 1);
        assert.deepEqual(state.activeCheckpoints, []);
        assert.equal(creditCheckpoint(state, canonical), false);
        assert.equal(state.clicksRemaining, 3);
    }
    assert.equal(Object.keys(resolved).length, 2);
    const state = game("Duffer_brothers", resolved, ["Rainbow flag (LGBT)"]);
    assert.equal(creditCheckpoint(state, "The Duffer Brothers"), true);
    assert.deepEqual(state.activeCheckpoints, ["Rainbow flag (LGBT)"]);
    assert.equal(creditCheckpoint(state, "Rainbow flag (LGBTQ)"), true);
});

test("lookup failures allow original-title play but reject submissions", async () => {
    for (const fetch of [
        async () => { throw new Error("offline"); },
        async () => ({ok: false}),
        async () => reply(undefined)
    ]) {
        globalThis.fetch = fetch;
        const resolved = await resolveCheckpointTitles(["Original", null]);
        assert.deepEqual(resolved, {});
        assert.equal(creditCheckpoint(game("Original", resolved), "Original"), true);
        await assert.rejects(validateCheckpoints(["Original"]));
    }
});

test("validation batches at 50, deduplicates lookups and preserves input order", async () => {
    const sizes = [];
    globalThis.fetch = async url => {
        const params = new URL(url).searchParams;
        assert.equal(params.get("ppprop"), "disambiguation");
        const titles = params.get("titles").split("|");
        sizes.push(titles.length);
        return reply({pages: titles.map(title => ({title, ns: 0})).reverse()});
    };
    const titles = Array.from({length: 51}, (_, i) => `Page ${i}`);
    assert.deepEqual(await validateCheckpoints([...titles, titles[0]]), [...titles, titles[0]]);
    assert.deepEqual(sizes, [50, 1]);
});

test("builder blocks missing, invalid, namespaced and disambiguation checkpoints", async () => {
    for (const page of [
        {title: "Bad", ns: 0, pageprops: {disambiguation: ""}},
        {title: "Bad", ns: 12}, {title: "Bad", missing: true}, {title: "Bad", invalid: true}
    ]) {
        globalThis.fetch = async () => reply({pages: [page]});
        const state = {...MarathonBuilder.data(), placeholder: "Bad", startcp: Array(5).fill("Bad"), cp: Array(40).fill("Bad")};
        await MarathonBuilder.methods.addArticle.call(state, 1);
        assert.equal(state.startcp.length, 5);
        assert.ok(state.articleCheckMessage);
        let submitted = false;
        state.submitAsCmty = async () => { submitted = true; };
        await MarathonBuilder.methods.submitPrompt.call(state);
        assert.equal(submitted, false);
        assert.ok(state.articleCheckMessage);
    }
    await assert.rejects(validateCheckpoints([""]), /empty/);
    await assert.rejects(validateCheckpoints([null]), /empty/);
});

test("minimum prompt submits in two requests and rejects aliases that become duplicates", async () => {
    let requests = 0;
    globalThis.fetch = async url => {
        requests++;
        const titles = new URL(url).searchParams.get("titles").split("|");
        return reply({redirects: [{from: "Old name", to: "Page 0"}],
            pages: titles.map(title => ({title: title === "Old name" ? "Page 0" : title, ns: 0}))});
    };
    const state = {...MarathonBuilder.data(), startcp: ["Old name", "Page 1", "Page 2", "Page 3", "Page 4"], cp: Array.from({length: 40}, (_, i) => `Page ${i + 5}`)};
    let submitted = 0;
    state.submitAsCmty = async () => { submitted++; };
    await MarathonBuilder.methods.submitPrompt.call(state);
    assert.equal(submitted, 1);
    assert.equal(requests, 2);
    assert.equal(state.startcp[0], "Page 0");
    state.cp[0] = "Old name";
    await MarathonBuilder.methods.submitPrompt.call(state);
    assert.equal(submitted, 1);
    assert.match(String(state.articleCheckMessage), /already exists/);
});

test("example builder stops after a rejected checkpoint", async () => {
    for (const cp of [[], Array(40).fill("Example")]) {
        let attempts = 0;
        const state = {cp, startcp: [], addArticle: async () => {
            attempts++;
            assert.equal(attempts, 1);
        }};
        await MarathonBuilder.methods.loadGeneric.call(state);
        assert.equal(attempts, 1);
    }
});
