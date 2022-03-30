

async function fetchJson(path, method='GET', body=null)
{
    let options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
    };

    if (body) {
        options.body = JSON.stringify(body)
    }

    return fetch(path, options);
}


async function fetchAsync(basePath, method='GET', body=null)
{
    const response = await fetchJson(basePath, method, body);

    if (response.status != 200) {
        console.log(await response.text());
        return null;
    }

    const task_id = (await response.json())['task_id'];

    return new Promise((resolve, reject) => {
        let interval = setInterval(async () => {
            const response = await fetchJson(basePath + "/result", "POST", {
                "task_id": task_id,
            });

            if (resp.status !== 200) {
                clearInterval(interval);
                reject("Unknown Error");
            }

            const resp = await response.json();

            if (resp["status"] === "error") {
                clearInterval(interval);
                reject(resp["error"]);
            }

            if (resp["status"] === "complete") {
                clearInterval(interval);
                resolve(resp["result"]);
            }
        }, 5000);
    });


}

export { fetchJson, fetchAsync };