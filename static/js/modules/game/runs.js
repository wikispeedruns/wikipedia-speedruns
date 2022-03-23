
import { fetchJson } from "../fetch.js";

async function startRun(promptId, lobbyId=null) {
    // No need to record unfinished private runs
    if (lobbyId) {
        return -1;
    }

    const response = await fetchJson("/api/runs", "POST", {
        "prompt_id": promptId,
    });
    return await response.json();
}

async function submitRun(promptId, lobbyId,  runId, startTime, endTime, path) {
    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "path": path,
    }

    if (lobbyId) {
        const response = await fetchJson(`/api/lobbys/${lobbyId}/prompts/${promptId}/runs`, 'POST', reqBody);
        return (await response.json())["run_id"];
    } else {
        // Send results to API
        const response = await fetchJson(`/api/runs/${runId}`, 'PATCH', reqBody);
        return runId;
    }
}

/*
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
}*/


export { startRun, submitRun };