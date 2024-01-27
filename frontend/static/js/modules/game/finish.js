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

export { getRun, getLobbyRun, getQuickRun};