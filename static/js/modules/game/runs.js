
import { fetchJson } from "../fetch.js";

// Send request to create an empty run, returns the run_id
async function startRun(prompt_id, lobby_id=null) {
    if (lobby_id === null) {
        // Don't bother creating a run for lobby prompts
        return -1;
    }

    const response = await fetchJson("/api/runs", "POST", {
        "prompt_id": prompt_id,
    });
    return await response.json();
}

async function submitRun(runId, startTime, endTime, path ) {
    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "path": path,
    }



    // Send results to API
    const response = await fetchJson(`/api/runs/${runId}`, 'PATCH', reqBody);
}


export { startRun, submitRun };