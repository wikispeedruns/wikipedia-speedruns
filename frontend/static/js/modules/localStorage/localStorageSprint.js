import {startRun, submitRun, updateAnonymousRun} from "../game/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"
import {startLocalQuickRun, submitLocalQuickRun } from "./localStorageQuickRun.js"

function startLocalRun(promptId, promptStart, promptEnd, runId, language) {
    if(promptId == null){
        startLocalQuickRun(promptStart, promptEnd, runId, language);
        return;
    }

    const data = {
        run_id: runId,
        prompt_id: promptId,
    };

    const key = "WS-S-sprint-runs";

    addRunToLocalStorage(key, data);
}

function submitLocalRun(promptId, promptStart, promptEnd, runId, startTime, endTime, finished, path, language) {
    if(promptId == null){
        submitLocalQuickRun(promptStart, promptEnd, runId, startTime, endTime, finished, path, language);
        return;
    }

    let data = {
        prompt_id: promptId,
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

function getLocalRun(run_id) {
    return getLocalSprints()[run_id];
}

export { startLocalRun, submitLocalRun, uploadLocalSprints, getLocalSprints, getLocalRun };

