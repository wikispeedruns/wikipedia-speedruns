import {startRun, submitRun, updateAnonymousRun} from "../game/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"

function startLocalRun(promptId, runId) {
    const data = {
        run_id: runId,
        prompt_id: promptId,
    };

    const key = "WS-S-sprint-runs";

    addRunToLocalStorage(key, data);
}

function submitLocalRun(promptId, runId, startTime, endTime, path) {
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

async function uploadLocalSprints() {
    const key = "WS-S-sprint-runs";
    let data = getLocalStorageRuns(key);

    const runs = Object.keys(data)
    if (runs.length == 0) return;

    let runIds = [];

    //console.log("Logged in, updating runs")

    for (let runId of runs) {
        try {
            await updateAnonymousRun(runId);
            runIds.push(runId);
            //console.log(`RUNID: ${runId}`)
        } catch (e) {
            console.log(e);
        }
    }
    //console.log("Removing sprint run cache")
    localStorage.removeItem(key);
}

function getLocalSprints() {
    const key = "WS-S-sprint-runs";
    return getLocalStorageRuns(key);
}

export { startLocalRun, submitLocalRun, uploadLocalSprints, getLocalSprints };

