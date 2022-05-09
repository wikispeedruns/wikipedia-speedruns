import { fetchJson } from "../fetch.js";

async function getUserLobby(loggedIn)
{
    if (!loggedIn) return []

    let lobbies = await fetchJson("/api/lobbys/getuserlobbys", "GET")
    return await lobbies.json()
}

export { getUserLobby };