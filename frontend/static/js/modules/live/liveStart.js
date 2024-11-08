// A very simple websocker client to signal people finishing a prompt
// and to tell the leaderboard to update

const wsServer = process.env.LIVE_WS_SERVER;

class LiveStartHelper {
    constructor(lobbyId, promptId, user, startCallback, updateUsersCallback) {
        this.ws = new WebSocket(wsServer);
        this.lobbyId = lobbyId;
        this.promptId = promptId;

        this.ws.onopen = (event) => {
            this.ws.send(JSON.stringify({
                type: "wait_start",
                lobby_id: lobbyId,
                prompt_id: promptId,
                user: user,
            }));
        }

        this.ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg["type"] === "start") {
                    startCallback();
                } else if (msg["type"] === "update") {
                    updateUsersCallback(msg["users"])
                }

            } catch (error) {
                console.error("Invalid JSON from websocket server:", error);
            }
        };
    }

    triggerStart() {
        this.ws.send(JSON.stringify({
            type: "start",
            lobby_id: this.lobbyId,
            prompt_id: this.promptId,
        }));
    }
}

export { LiveStartHelper };