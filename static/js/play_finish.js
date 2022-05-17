//JS module imports
import { serverData } from "./modules/serverData.js";
import { getRun, getLobbyRun } from "./modules/game/finish.js";

import { basicCannon, fireworks, side } from "./modules/confetti.js";

// Get lobby if a lobby_prompt
const LOBBY_ID = serverData["lobby_id"] || null;
const PLAYED = serverData["played"] || false;
const RUN_ID = serverData["run_id"] || null;

async function getPrompt(promptId, lobbyId=null) {
    const url = (lobbyId === null) ? `/api/sprints/${promptId}` : `/api/lobbys/${lobbyId}/prompts/${promptId}`;
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


//Vue container. This contains data, rendering flags, and functions tied to game logic and rendering. See play.html
let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        startArticle: "",    // For all game modes, this is the first article to load
        endArticle: "",      // For sprint games. Reaching this article will trigger game finishing sequence
        path: [],             // array to store the user's current path so far, submitted with run

        promptId: null,        //Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display

        lobbyId: null,
        runId: null,          //unique ID for the current run. This gets populated upon start of run

        startTime: null,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        playTime: 0,
        loggedIn: false,

        played: PLAYED
    },

    mounted: async function() {

        this.loggedIn = "username" in serverData;

        this.lobbyId = LOBBY_ID;
        this.runId = RUN_ID;

        let run = null;
        if (this.lobbyId != null) {
            run = await getLobbyRun(this.lobbyId, RUN_ID);
        } else {
            run = await getRun(RUN_ID);
        }

        this.promptId = run['prompt_id'];
        const prompt = await getPrompt(this.promptId, LOBBY_ID);

        this.startArticle = prompt["start"];
        this.endArticle = prompt["end"];
        this.playTime = run["play_time"];

        this.path = run['path'].map((entry) => entry["article"])

        if (this.played) fireworks();

    },


    methods: {
        //copy sharable result
        copyResults: function(event) {
            let results = this.generateResults();
            document.getElementById("custom-tooltip").style.display = "inline";
            document.getElementById("custom-tooltip-path").style.display = "none";
            navigator.clipboard.writeText(results);
            setTimeout(function() {
                document.getElementById("custom-tooltip").style.display = "none";
            }, 1500);
        },

        //copy sharable result
        copyPath: function(event) {
            let results = this.generatePath();
            document.getElementById("custom-tooltip-path").style.display = "inline";
            document.getElementById("custom-tooltip").style.display = "none";
            navigator.clipboard.writeText(results);
            setTimeout(function() {
                document.getElementById("custom-tooltip-path").style.display = "none";
            }, 1500);
        },

        //go back to home page
        home: function (event) {
            window.location.replace("/");
        },

        goToLobby: function (event) {
            window.location.replace(`/lobby/${this.lobbyId}`);
        },


        generateResults: function(event) {
            return `Wiki Speedruns ${this.promptId}\n${this.startArticle}\n${this.path.length - 1} 🖱️\n${(this.playTime)} ⏱️`
        },

        generatePath: function(event) {
            return String(this.path);
        },

        //redirect to the corresponding prompt page
        goToLobbyLeaderboard: function (event) {
            window.location.replace(`/lobby/${this.lobbyId}/prompt/${this.promptId}?run_id=${this.runId}`);
        },
    }
})

