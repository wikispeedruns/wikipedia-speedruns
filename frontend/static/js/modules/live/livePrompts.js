// A very simple websocker client to signal people finishing a prompt
// and to tell the leaderboard to update

const wsServer = process.env.LIVE_WS_SERVER;



class LiveLobbyPromptsHelper {
    constructor(lobbyId, updateCallback) {
        this.ws = new WebSocket(wsServer);
        this.lobbyId = lobbyId;

        this.ws.onopen = (event) => {
            this.ws.send(JSON.stringify({
                type: "lobby_prompts",
                lobby_id: lobbyId,
            }));
        }

        this.ws.onmessage = (event) => {
            if (event.data === "refresh") {
                updateCallback()
            }
        };
    }

    triggerUpdate() {  
        
        console.log(`Trigger update ${this.lobbyId}`);

        this.ws.send(JSON.stringify({
            type: "lobby_prompts_update",
            lobby_id: this.lobbyId,
        }));

    };
}

export {LiveLobbyPromptsHelper};