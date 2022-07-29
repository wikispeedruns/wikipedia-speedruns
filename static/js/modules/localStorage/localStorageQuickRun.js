import {startRun, submitRun, updateAnonymousRun} from "../game/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"

function startLocalQuickRun(promptStart, promptEnd, runId) {
    const data = {
        run_id: runId,
        prompt_start: promptStart,
        prompt_end: promptEnd
    };

    const key = "WS-S-quick-runs";

    addRunToLocalStorage(key, data);
}

function submitLocalQuickRun(promptStart, promptEnd, runId, startTime, endTime, finished, path) {
    let data = {
        prompt_start: promptStart,
        prompt_end: promptEnd,
        start_time: startTime,
        end_time: endTime,
        finished: finished,
        path: path
    };

    let totalloadtime = -path[0]['loadTime'] + path[0]['timeReached'];
    path.forEach(function (el) {
        totalloadtime += el['loadTime']
    });
    data['play_time'] = (endTime - startTime) / 1000 - totalloadtime;

    const key = "WS-S-quick-runs";

    let ls = getLocalStorageRuns(key);
    ls[runId] = data;
    setLocalStorageRuns(key, ls);

    //console.log(getLocalStorageRuns(key));
}

async function uploadLocalQuickRuns() {
    const key = "WS-S-quick-runs";
    let data = getLocalStorageRuns(key);

    const runs = Object.keys(data)
    if (runs.length == 0) return;

    let runIds = [];

    //console.log("Logged in, updating runs")

    for (let runId of runs) {
        try {
            await updateAnonymousRun(runId, type = "quick");
            runIds.push(runId);
            //console.log(`RUNID: ${runId}`)
        } catch (e) {
            console.log(e);
        }
    }
    //console.log("Removing sprint run cache")
    localStorage.removeItem(key);
}

function getLocalQuickRuns() {
    const key = "WS-S-quick-runs";
    return getLocalStorageRuns(key);
}

function getLocalQuickRun(run_id) {
    return getLocalQuickRuns()[run_id];
}

export { startLocalQuickRun, submitLocalQuickRun, uploadLocalQuickRuns, getLocalQuickRuns, getLocalQuickRun };

