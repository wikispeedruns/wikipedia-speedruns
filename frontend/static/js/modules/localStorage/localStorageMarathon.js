import { submitRun, updateAnonymousRun } from "../game/marathon/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"

function submitLocalRun(run_id, prompt_id, time, checkpoints, path, finished) {
    const data = {
        "run_id": run_id,
        "path": path,
        "checkpoints": checkpoints,
        "prompt_id": prompt_id,
        "time": time,
        "finished": finished
    };

    const key = "WS-LM-marathonruns";

    addRunToLocalStorage(key, data);
}

async function uploadLocalMarathons() {
    const key = "WS-LM-marathonruns";
    let data = getLocalStorageRuns(key);

    const runs = Object.keys(data)
    if (runs.length == 0) return;

    let runIds = [];

    for (let runId of runs) {
        try {
            await updateAnonymousRun(runId);
            runIds.push(runId);
        } catch (e) {
            console.log(e);
        }
    }

    localStorage.removeItem(key);
}

function getLocalMarathons() {
    const key = "WS-LM-marathonruns";
    return getLocalStorageRuns(key);
}

export { submitLocalRun, uploadLocalMarathons, getLocalMarathons };
