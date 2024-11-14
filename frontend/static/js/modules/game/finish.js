import { fetchJson } from "../fetch.js";

async function getRun(runId) {
    try {
        const response = await fetchJson(`/api/runs/${runId}`, 'GET');
        const body = await response.json();
        return body;
    } catch (e) {
        console.log(e);
    }
}

async function getLobbyRun(lobbyId, runId) {
    try {
        const response = await fetchJson(`/api/lobbys/${lobbyId}/run/${runId}`, 'GET');
        const body = await response.json();
        return body;
    } catch (e) {
        console.log(e);
    }
}

async function getQuickRun(runId) {
    try {
        const response = await fetchJson(`/api/quick_run/runs/${runId}`, 'GET');
        const body = await response.json();
        return body;
    } catch (e) {
        console.log(e);
    }
}

async function getLobby(lobbyId) {
    const url = `/api/lobbys/${lobbyId}`;
    const response = await fetch(url);

    if (response.status != 200) {
        const error = await response.text();
        alert(error);

        // Prevent are you sure you want to leave prompt
        window.onbeforeunload = null;
        window.location.replace("/");   // TODO error page
        return;
    }

    return await response.json();
}

export { getRun, getLobbyRun, getQuickRun, getLobby};