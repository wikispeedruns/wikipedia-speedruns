
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

async function updateAnonymousRun(runId) {
    const reqBody = {
        "run_id": parseInt(runId)
    };

    try {
        const response = await fetchJson(`/api/runs/update_anonymous`, 'PATCH', reqBody);
    } catch (e) {
        console.log(e);
    }
}


export { startRun, submitRun, updateAnonymousRun };