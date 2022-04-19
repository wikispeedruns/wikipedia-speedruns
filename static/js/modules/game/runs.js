import { sendBeaconJson } from "../beacon.js";
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

async function submitRun(promptId, lobbyId,  runId, startTime, endTime, finished, path, beacon=false) {
    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "finished": finished,
        "path": path,
    }

    if (lobbyId) {
        if (beacon) {
            sendBeaconJson(`/api/lobbys/${lobbyId}/prompts/${promptId}/runs`, reqBody);
        } else {
        const response = await fetchJson(`/api/lobbys/${lobbyId}/prompts/${promptId}/runs`, 'POST', reqBody);
        return (await response.json())["run_id"];
        }
    } else {
        if (beacon) {
            sendBeaconJson(`/api/runs/${runId}`, reqBody);
        } else {
            const response = await fetchJson(`/api/runs/${runId}`, 'POST', reqBody);
        return runId;
        }
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