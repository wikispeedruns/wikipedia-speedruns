import { fetchJson } from "../fetch.js";

async function startRun(promptId, lobbyId, startTime) {
    const reqBody = {
        "start_time": startTime,
    };

    let endpoint = lobbyId == null
        ? "/api/runs"
        : `/api/lobbys/${lobbyId}/prompts/${promptId}/runs`;

    const response = await fetchJson(endpoint, "POST", {
        "prompt_id": promptId,
    });
    return (await response.json())["run_id"];
}

async function submitRun(promptId, lobbyId,  runId, startTime, endTime, finished, path) {
    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "finished": finished,
        "path": path,
    }

    let endpoint = lobbyId == null
        ? `/api/runs/${runId}`
        : `/api/lobbys/${lobbyId}/prompts/${promptId}/runs/${runId}`;

    const response = await fetchJson(endpoint, "PATCH", {
        "prompt_id": promptId,
    });
    return (await response.json())["run_id"];
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


export { startRun, submitRun, updateAnonymousRun};