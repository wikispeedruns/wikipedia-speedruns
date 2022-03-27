import { submitRun } from "../game/marathon/runs.js"
import { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns } from "./localStorage.js"

function submitLocalRun(prompt_id, time, checkpoints, path, finished) {
    const data = {
        "path": path,
        "checkpoints": checkpoints,
        "prompt_id": prompt_id,
        "time": time,
        "finished": finished
    };

    const key = "WS-LM-marathonruns";

    return addRunToLocalStorage(key, data);
}

async function uploadLocalMarathons() {
    const key = "WS-LM-marathonruns";
    let data = getLocalStorageRuns(key);

    if (Object.keys(data).length == 0) return;

    let runIds = [];

    for (const k in data) {
        const run = data[k]
        try {
            const runId = await submitRun(run.prompt_id, 
                                        run.time,
                                        run.checkpoints, 
                                        run.path, 
                                        run.finished );
            runIds.push(runId);
        } catch (e) {
            console.log(e);
        }
    }

    console.log("Finished uploading runIds: ")
    console.log(runIds)
    console.log("Removing marathon run cache")

    localStorage.removeItem(key);
}

export { submitLocalRun, uploadLocalMarathons };
