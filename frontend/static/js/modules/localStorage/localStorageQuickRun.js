import {startRun, submitRun, updateAnonymousRun} from "../game/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"

const location = "WS-S-quick-runs"

function startLocalQuickRun(promptStart, promptEnd, runId, language) {
    const data = {
        run_id: runId,
        prompt_start: promptStart,
        prompt_end: promptEnd,
        language: language,
    };

    const key = location;

    addRunToLocalStorage(key, data);
}

function submitLocalQuickRun(promptStart, promptEnd, runId, startTime, endTime, finished, path, language) {
    let data = {
        prompt_start: promptStart,
        prompt_end: promptEnd,
        language: language,
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

    const key = location;

    let ls = getLocalStorageRuns(key);
    ls[runId] = data;
    setLocalStorageRuns(key, ls);

    //console.log(getLocalStorageRuns(key));
}

async function uploadLocalQuickRuns() {
    const key = location;
    let data = getLocalQuickRuns();

    const runs = Object.keys(data)
    if (runs.length == 0) return;

    let runIds = [];

    for (let runId of runs) {
        try {
            await updateAnonymousRun(runId, "quick");
            runIds.push(runId);
            //console.log(`RUNID: ${runId}`)
        } catch (e) {
            console.log(e);
        }
    }

    //console.log("Removing quick run cache")
    localStorage.removeItem(key);
}

function getLocalQuickRuns() {
    const key = location;
    return getLocalStorageRuns(key);
}

function getLocalQuickRun(run_id) {
    return getLocalQuickRuns()[run_id];
}

export { startLocalQuickRun, submitLocalQuickRun, uploadLocalQuickRuns, getLocalQuickRuns, getLocalQuickRun };

