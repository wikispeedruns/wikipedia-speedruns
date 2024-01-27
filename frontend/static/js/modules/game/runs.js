import { fetchJson } from "../fetch.js";

async function startRun(promptId, lobbyId, promptStart, promptEnd, language) {

    let endpoint = null;
    if(promptId == null) {
        endpoint = `/api/quick_runs/runs?prompt_start=${promptStart}&prompt_end=${promptEnd}&lang=${language}`;
    }
    else if(lobbyId == null) endpoint = `/api/sprints/${promptId}/runs`;
    else endpoint = `/api/lobbys/${lobbyId}/prompts/${promptId}/runs`;
    
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

    let endpoint = null;
    if(promptId == null) endpoint = `/api/quick_runs/runs/${runId}`;
    else if(lobbyId == null) endpoint = `/api/sprints/${promptId}/runs/${runId}`
    else endpoint = `/api/lobbys/${lobbyId}/prompts/${promptId}/runs/${runId}`;
    
    const response = await fetchJson(endpoint, "PATCH", reqBody);
    return (await response.json())["run_id"];
}

async function updateAnonymousRun(runId, type="sprint") {
    const reqBody = {
        "run_id": parseInt(runId)
    };

    try {
        const endpoint = (type == "sprint") ?
        `/api/runs/update_anonymous` : `/api/quick_runs/update_anonymous`;

        const response = await fetchJson(endpoint, 'PATCH', reqBody);
    } catch (e) {
        console.log(e);
    }
}


export { startRun, submitRun, updateAnonymousRun};