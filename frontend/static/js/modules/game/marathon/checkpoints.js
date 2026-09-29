function normalizeCheckpoint(title) {
    return typeof title === "string" ? title.replace(/_/g, " ").trim().toLowerCase() : "";
}

async function getCheckpointPages(titles) {
    const result = Object.create(null);
    const unique = [...new Set(titles)];
    for (let offset = 0; offset < unique.length; offset += 50) {
        const batch = unique.slice(offset, offset + 50);
        const response = await fetch(`https://en.wikipedia.org/w/api.php?action=query&redirects=1&origin=*&format=json&formatversion=2&prop=pageprops&ppprop=disambiguation&titles=${encodeURIComponent(batch.join("|"))}`, {mode: "cors", signal: AbortSignal.timeout(8000)});
        if (!response.ok) throw new Error("Checkpoint title lookup failed");
        const body = await response.json();
        if (!body.query?.pages) throw new Error("Missing checkpoint titles");
        const aliases = new Map([...(body.query.normalized || []), ...(body.query.redirects || [])].map(alias => [alias.from, alias.to]));
        const pages = new Map(body.query.pages.map(page => [page.title, page]));
        for (const title of batch) {
            let canonical = title;
            const seen = new Set();
            while (aliases.has(canonical) && !seen.has(canonical)) {
                seen.add(canonical);
                canonical = aliases.get(canonical);
            }
            result[title] = pages.get(canonical);
        }
    }
    return result;
}

// Keep stored labels/save files intact; lookup failures must not prevent play.
export async function resolveCheckpointTitles(titles) {
    try {
        const pages = await getCheckpointPages(titles.filter(title => normalizeCheckpoint(title)));
        return Object.fromEntries(Object.entries(pages)
            .filter(([, page]) => page && !page.missing && !page.invalid)
            .map(([title, page]) => [title, page.title]));
    } catch (error) {
        console.warn("Could not resolve checkpoint titles; using stored titles", error);
        return {};
    }
}

export async function validateCheckpoints(titles) {
    if (titles.some(title => !normalizeCheckpoint(title))) throw new Error("Checkpoint is empty");
    const pages = await getCheckpointPages(titles);
    return titles.map(title => {
        const page = pages[title];
        if (!page || page.missing || page.invalid) throw new Error(`"${title}" is not a Wikipedia article`);
        if (page.ns !== 0) throw new Error(`"${title}" is a namespaced article`);
        if (page.pageprops && "disambiguation" in page.pageprops) throw new Error(`"${title}" is a disambiguation page`);
        return page.title;
    });
}

export function creditCheckpoint(game, page) {
    const normalizedPage = normalizeCheckpoint(page);
    if (!normalizedPage) return false;
    const index = game.activeCheckpoints.findIndex(title => normalizeCheckpoint(title) &&
        normalizedPage === normalizeCheckpoint(game.resolvedCheckpointTitles[title] || title));
    if (index === -1) return false;
    game.clicksRemaining += game.clicksPerCheckpoint + 1;
    game.visitedCheckpoints.push(page);
    const next = game.checkpoints.shift();
    if (next) game.activeCheckpoints.splice(index, 1, next);
    else game.activeCheckpoints.splice(index, 1);
    return true;
}
