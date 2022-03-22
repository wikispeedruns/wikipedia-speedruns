import { fetchJson } from './fetch.js'


async function getPath(start, end) {
    const response = await fetchJson("/api/scraper/path", "POST", {
        "start": start,
        "end": end
    });

    if (response.status != 200) {
        console.log(await response.text());
        return null;
    }

    const path = await response.json();

    return path['task_id'];
}


export { getPath };