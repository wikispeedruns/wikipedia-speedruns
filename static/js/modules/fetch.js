

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

export { fetchJson };