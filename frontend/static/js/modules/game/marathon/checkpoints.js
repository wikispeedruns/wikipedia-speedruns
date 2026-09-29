import { getArticleTitle, articleCheck } from "../../wikipediaAPI/util.js";

export function normalizeCheckpoint(title) {
    return typeof title === "string" ? title.replace(/_/g, " ").trim().toLowerCase() : "";
}

// Resolve in batches before the timer starts. Keep stored labels/save files intact.
export async function resolveCheckpointTitles(titles) {
    const resolved = Object.create(null);
    const unique = [...new Set(titles.filter(title => typeof title === "string" && title.trim()))];
    for (let offset = 0; offset < unique.length; offset += 50) {
        const batch = unique.slice(offset, offset + 50);
        try {
            const response = await fetch(`https://en.wikipedia.org/w/api.php?action=query&redirects=1&origin=*&format=json&formatversion=2&titles=${encodeURIComponent(batch.join("|"))}`, {mode: "cors", signal: AbortSignal.timeout(8000)});
            if (!response.ok) throw new Error("Checkpoint title lookup failed");
            const body = await response.json();
            if (!body.query?.pages) throw new Error("Missing checkpoint titles");
            const aliases = new Map([...(body.query.normalized || []), ...(body.query.redirects || [])].map(alias => [alias.from, alias.to]));
            const pages = new Set(body.query.pages.filter(page => !page.missing && !page.invalid).map(page => page.title));
            for (const title of batch) {
                let canonical = title;
                const seen = new Set();
                while (aliases.has(canonical) && !seen.has(canonical)) {
                    seen.add(canonical);
                    canonical = aliases.get(canonical);
                }
                if (pages.has(canonical)) resolved[title] = canonical;
            }
        } catch (error) {
            console.warn("Could not resolve checkpoint titles; using stored titles", error);
        }
    }
    return resolved;
}

export function findCheckpoint(page, checkpoints, resolved = {}) {
    const normalizedPage = normalizeCheckpoint(page);
    if (!normalizedPage) return -1;
    return checkpoints.findIndex(title => normalizeCheckpoint(title) &&
        normalizedPage === normalizeCheckpoint(resolved[title] || title));
}

export async function validateCheckpoint(title) {
    if (typeof title !== "string" || !title.trim()) throw new Error("Checkpoint is empty");
    const canonical = await getArticleTitle(title);
    if (!canonical) throw new Error(`"${title}" is not a Wikipedia article`);
    const result = await articleCheck(canonical);
    if (result.warning) throw new Error(result.warning);
    return canonical;
}
