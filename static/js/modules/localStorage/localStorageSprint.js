import {startRun, submitRun} from "../game/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"

function addSprintRunToLocalStorage(promptId) {
    const data = {
        prompt_id: promptId,
    };

    const key = "WS-S-sprint-runs";

    return addRunToLocalStorage(key, data);
}

function submitSprintRunToLocalStorage(promptId, runId, startTime, endTime, path) {
    let data = {
        prompt_id: promptId,
        start_time: startTime,
        end_time: endTime,
        path: path
    };

    const key = "WS-S-sprint-runs";

    let ls = getLocalStorageRuns(key);
    ls[runId] = data;
    setLocalStorageRuns(key, ls);

    //console.log(getLocalStorageRuns(key));
}

async function uploadAllLocalStorageSprintRuns() {
    const key = "WS-S-sprint-runs";
    let data = getLocalStorageRuns(key);

    if (Object.keys(data).length == 0) return;

    let runIds = [];

    for (const k in data) {
        const run = data[k]
        //console.log(run)
        try {
            const runId = await startRun(run.prompt_id);
            runIds.push(runId);
            await submitRun(run.prompt_id, 
                            null, 
                            runId, 
                            run.start_time, 
                            run.end_time, 
                            run.path );
        } catch (e) {
            console.log(e);
        }
    }

    console.log("Finished uploading runIds: ")
    console.log(runIds)
    console.log("Removing sprint run cache")

    localStorage.removeItem(key);
}

export { addSprintRunToLocalStorage, submitSprintRunToLocalStorage, uploadAllLocalStorageSprintRuns };

