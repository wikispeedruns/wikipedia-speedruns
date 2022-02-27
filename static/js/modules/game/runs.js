
//send request to create an empty run, returns the run_id
async function startRun(prompt_id) {
    const reqBody = {
        "prompt_id": prompt_id,
    }
    try {
        const response = await fetch("/api/runs", {
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

async function submitRun(runId, startTime, endTime, path ) {
    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "path": path,
    }

    // Send results to API
    try {
        const response = await fetch(`/api/runs/${runId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

    } catch(e) {
        console.log(e);
    }
}


export { startRun, submitRun };