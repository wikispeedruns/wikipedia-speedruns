import { fetchJson } from "../../fetch.js";

async function saveRun(data) {
    const reqBody = {
        "path": data.path,
        "visited_checkpoints": data.visitedCheckpoints,
        "active_checkpoints": data.activeCheckpoints,
        "remaining_checkpoints": data.checkpoints,
        "prompt_id": data.promptId,
        "time": data.endTime - data.startTime + data.lastTime,
        "clicks_remaining": data.clicksRemaining,
    }
    //console.log(reqBody)

    localStorage.setItem('WS-M-'+String(data.promptId), JSON.stringify(reqBody))

    return reqBody
}

function loadRun(id) {
    return JSON.parse(localStorage.getItem('WS-M-'+String(id)))
}

function removeSave(id) {
    localStorage.removeItem('WS-M-'+String(id))
}

async function submitRun(prompt_id, time, checkpoints, path, finished) {

    //console.log(time)

    const reqBody = {
        "path": path,
        "checkpoints": checkpoints,
        "prompt_id": prompt_id,
        "time": time,
        "finished": finished
    }

    // Send results to API
    try {
        const response = await fetch(`/api/marathon/runs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

        return await response.json();

    } catch(e) {
        console.log(e);
    }
}

async function updateAnonymousRun(runId) {
    const reqBody = {
        "run_id": parseInt(runId)
    };

    try {
        const response = await fetchJson(`/api/marathon/update_anonymous`, 'PATCH', reqBody);
    } catch (e) {
        console.log(e);
    }
}


export { submitRun, saveRun, loadRun, removeSave, updateAnonymousRun };