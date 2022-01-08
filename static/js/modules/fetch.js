

export async function fetchJson(path, method='GET', body=null)
{

    if (body) {
        const response = await fetch(path, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
        return await response.json();

    } else {
        const response = await fetch(path, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        })
        return await response.json();

    }

}