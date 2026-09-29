const { test } = require("node:test");
const assert = require("node:assert/strict");
const { buildSync, transformSync } = require("esbuild");
const { readFileSync } = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = path.resolve(__dirname, "../..");

function loadModule(relative, overrides = {}) {
    const source = buildSync({entryPoints: [path.join(root, relative)], bundle: true, write: false, platform: "node", format: "cjs"}).outputFiles[0].text;
    const context = {module: {exports: {}}, AbortSignal, console: {warn() {}}, ...overrides};
    vm.runInNewContext(source, context);
    return context.module.exports;
}
const helperPath = "frontend/static/js/modules/game/marathon/checkpoints.js";
const reply = body => ({ok: true, json: async () => body});

test("stored aliases, normalization and redirect chains match canonical pages", async () => {
    let request;
    const helper = loadModule(helperPath, {fetch: async url => {
        request = new URL(url);
        return reply({query: {
            normalized: [{from: "Duffer_brothers", to: "Duffer brothers"}],
            redirects: [{from: "Duffer brothers", to: "Duffer Brothers"}, {from: "Duffer Brothers", to: "The Duffer Brothers"}],
            pages: [{title: "The Duffer Brothers"}]
        }});
    }});
    const resolved = await helper.resolveCheckpointTitles(["Duffer_brothers"]);
    assert.equal(request.searchParams.get("titles"), "Duffer_brothers");
    assert.equal(helper.findCheckpoint("The Duffer Brothers", ["Duffer_brothers"], resolved), 0);
    assert.equal(helper.findCheckpoint("the_Duffer_Brothers", ["Duffer_brothers"], resolved), 0);
    assert.equal(helper.findCheckpoint("Duffer", ["Duffer_brothers"], resolved), -1);
    assert.equal(helper.findCheckpoint("Anything", [undefined, null], resolved), -1);
});

test("lookup failure and missing pages retain original matching", async () => {
    for (const fetch of [async () => {throw new Error("offline");}, async () => reply({error: {code: "bad"}}), async () => reply({query: {pages: [{title: "Gone", missing: true}]}})]) {
        const helper = loadModule(helperPath, {fetch});
        const resolved = await helper.resolveCheckpointTitles(["Gone", null]);
        assert.equal(Object.keys(resolved).length, 0);
        assert.equal(helper.findCheckpoint("Gone", ["Gone"], resolved), 0);
    }
});

test("batches stay within Wikipedia's 50-title limit and deduplicate", async () => {
    const sizes = [];
    const helper = loadModule(helperPath, {fetch: async url => {
        const titles = new URL(url).searchParams.get("titles").split("|");
        sizes.push(titles.length);
        return reply({query: {pages: titles.map(title => ({title}))}});
    }});
    const titles = Array.from({length: 51}, (_, i) => `Page ${i}`);
    const result = await helper.resolveCheckpointTitles([...titles, titles[0]]);
    assert.deepEqual(sizes, [50, 1]);
    assert.equal(Object.keys(result).length, 51);
});

test("checkpoint validation rejects disambiguation, missing and namespace pages", async () => {
    for (const page of [{title: "Prompt", ns: 0, pageprops: {disambiguation: ""}}, {title: "Help:Test", ns: 12}, {title: "Missing", missing: true}]) {
        const helper = loadModule(helperPath, {fetch: async () => reply({query: {pages: [page]}})});
        await assert.rejects(helper.validateCheckpoint(page.title));
    }
    const helper = loadModule(helperPath, {fetch: async () => reply({query: {pages: [{title: "The Duffer Brothers", ns: 0}]}})});
    assert.equal(await helper.validateCheckpoint("Duffer brothers"), "The Duffer Brothers");
});

function loadOptions(relative, helper) {
    const source = transformSync(readFileSync(path.join(root, relative), "utf8"), {format: "cjs"}).code;
    let options;
    const confetti = {create: () => () => {}};
    const context = {
        module: {exports: {}}, serverData: {}, setInterval: () => 1,
        window: {addEventListener() {}, scrollTo() {}},
        document: {getElementById: () => ({style: {}})},
        require: name => {
            if (name.includes("vue")) return function Vue(value) {options = value;};
            if (name.includes("checkpoints.js")) return helper;
            if (name === "canvas-confetti") return confetti;
            return {};
        }
    };
    vm.runInNewContext(source, context);
    return options || context.module.exports.MarathonBuilder;
}

test("real marathon callback credits redirected checkpoint once and exhausts reserves safely", () => {
    const helper = loadModule(helperPath);
    const options = loadOptions("frontend/static/js/pages/marathon.js", helper);
    const game = {...options.data, activeCheckpoints: ["Duffer brothers"], checkpoints: [], path: ["Stranger Things"], visitedCheckpoints: [], resolvedCheckpointTitles: {"Duffer brothers": "The Duffer Brothers"}, clicksRemaining: 3, clicksPerCheckpoint: 5, hidePreview() {}};
    options.methods.pageCallback.call(game, "The Duffer Brothers", 10);
    assert.equal(game.clicksRemaining, 8);
    assert.equal(game.visitedCheckpoints.length, 1);
    assert.equal(game.activeCheckpoints.length, 0);
    options.methods.pageCallback.call(game, "The Duffer Brothers", 10);
    assert.equal(game.clicksRemaining, 8);
    options.methods.pageCallback.call(game, "Other article", 10);
    assert.equal(game.clicksRemaining, 7);
});

test("builder rejects invalid targets on add and preloaded submission", async () => {
    const helper = {validateCheckpoint: async () => {throw new Error("disambiguation");}};
    const builder = loadOptions("frontend/static/js/modules/prompts/marathon-submit.js", helper);
    const state = {placeholder: "Prompt", startcp: [], cp: []};
    await builder.methods.addArticle.call(state, 1);
    assert.equal(state.startcp.length, 0);
    assert.equal(state.articleCheckMessage, "disambiguation");
    let submitted = false;
    state.startcp = Array(5).fill("Prompt");
    state.cp = Array(40).fill("Other");
    state.submitAsCmty = async () => {submitted = true;};
    await builder.methods.submitPrompt.call(state);
    assert.equal(submitted, false);
});


test("start resolves both restored active and reserve checkpoints before loading a page", async () => {
    let resolve;
    let requested;
    let loaded = false;
    const helper = {resolveCheckpointTitles: titles => {
        requested = titles;
        return new Promise(done => {resolve = done;});
    }};
    const options = loadOptions("frontend/static/js/pages/marathon.js", helper);
    const game = {...options.data, activeCheckpoints: ["Duffer brothers"], checkpoints: ["Prompt"], startArticle: "Alexander the Great", renderer: {loadPage: async () => {loaded = true;}}};
    const starting = options.methods.start.call(game);
    assert.equal(loaded, false);
    assert.equal(game.startTime, 0);
    assert.deepEqual(Array.from(requested), ["Duffer brothers", "Prompt"]);
    resolve({"Duffer brothers": "The Duffer Brothers"});
    await starting;
    assert.equal(loaded, true);
    assert.equal(game.resolvedCheckpointTitles["Duffer brothers"], "The Duffer Brothers");
});


test("Red Sea marathon credits its renamed final rainbow flag checkpoint", async () => {
    const helper = loadModule(helperPath, {fetch: async () => reply({query: {
        redirects: [{from: "Rainbow flag (LGBT)", to: "Rainbow flag (LGBTQ)"}],
        pages: [{pageid: 12813031, ns: 0, title: "Rainbow flag (LGBTQ)"}]
    }})});
    const resolved = await helper.resolveCheckpointTitles(["Rainbow flag (LGBT)"]);
    const options = loadOptions("frontend/static/js/pages/marathon.js", helper);
    const game = {...options.data, activeCheckpoints: ["Rainbow flag (LGBT)"], checkpoints: [], path: ["Rainbow flag"], visitedCheckpoints: [], resolvedCheckpointTitles: resolved, clicksRemaining: 1, clicksPerCheckpoint: 2, hidePreview() {}};
    options.methods.pageCallback.call(game, "Rainbow flag (LGBTQ)", 10);
    assert.equal(game.clicksRemaining, 3);
    assert.equal(game.visitedCheckpoints[0], "Rainbow flag (LGBTQ)");
    assert.equal(game.activeCheckpoints.length, 0);
    options.methods.pageCallback.call(game, "Rainbow flag (LGBTQ)", 10);
    assert.equal(game.visitedCheckpoints.length, 1);
    assert.equal(game.clicksRemaining, 3);
});


test("example builder stops when checkpoint validation rejects an article", async () => {
    const builder = loadOptions("frontend/static/js/modules/prompts/marathon-submit.js", {});
    for (const cp of [[], Array(40).fill("Example")]) {
        let attempts = 0;
        const state = {cp, startcp: [], addArticle: async () => {
            attempts += 1;
            assert.equal(attempts, 1, "must not repeatedly retry a rejected article");
        }};
        await builder.methods.loadGeneric.call(state);
        assert.equal(attempts, 1);
    }
});
