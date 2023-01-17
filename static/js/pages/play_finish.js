//JS module imports
import Vue from 'vue/dist/vue.esm.js';

import { getRun, getLobbyRun, getQuickRun } from "../modules/game/finish.js";
import { getLocalRun } from "../modules/localStorage/localStorageSprint.js"
import { getLocalQuickRun } from "../modules/localStorage/localStorageQuickRun.js";
import { achievements } from "../modules/achievements.js";
import { uploadLocalSprints } from "../modules/localStorage/localStorageSprint.js";

import { basicCannon, fireworks, side } from "../modules/confetti.js";

// Get lobby if a lobby_prompt
const LOBBY_ID = serverData["lobby_id"] || null;
const PLAYED = serverData["played"] || false;
const RUN_ID = serverData["run_id"] || null;
const TYPE = serverData["type"];

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
    components: {
        'achievements': achievements
    },

    data: {

        runType: "",         // the type of run (lobby, sprint, quick)

        startArticle: "",    // For all game modes, this is the first article to load
        endArticle: "",      // For sprint games. Reaching this article will trigger game finishing sequence
        language: "",        // For quick play and lobbies
        path: [],             // array to store the user's current path so far, submitted with run

        promptId: null,        //Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display

        lobbyId: null,
        runId: RUN_ID,          //unique ID for the current run. This gets populated upon start of run

        startTime: null,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        playTime: 0,
        loggedIn: false,

        played: PLAYED,

        isMounted: false
    },

    computed: {
        isSprint() {
            return this.runType == 'sprint';
        },
        isQuickRun() {
            return this.runType == 'quick';
        },
        isLobbyRun() {
            return this.runType == 'lobby';
        }
    },

    mounted: async function() {

        this.runType = TYPE;

        this.loggedIn = "username" in serverData;

        // Make sure that a sprint can be considered for achievements
        if (this.loggedIn) {
            await uploadLocalSprints();
        }

        this.lobbyId = LOBBY_ID;
        this.runId = RUN_ID;

        let run = null;
        if (this.isLobbyRun) {
            run = await getLobbyRun(this.lobbyId, RUN_ID);
        } else if (this.loggedIn) {
            run = this.isSprint ? await getRun(RUN_ID) : await getQuickRun(RUN_ID);
        } else if (!this.loggedIn) {
            run = this.isSprint ? getLocalRun(RUN_ID) : getLocalQuickRun(RUN_ID);
        }

        if(this.isQuickRun){
            this.startArticle = run["prompt_start"];
            this.endArticle = run["prompt_end"];
            this.language = run['language'];
        }
        else{
            this.promptId = run['prompt_id'];
            const prompt = await getPrompt(this.promptId, LOBBY_ID);

            this.startArticle = prompt["start"];
            this.endArticle = prompt["end"];
            this.language = prompt["language"];
        }

        this.playTime = run["play_time"];

        this.path = run['path'].map((entry) => entry["article"])

        if (this.played) fireworks();

        this.isMounted = true;
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

        quickPlay: function (event) {
            window.location.replace("/#quick-play");
        },


        generateResults: function(event) {
            let resultText = `Wiki Speedruns\n${this.startArticle}\n${this.path.length - 1} 🖱️\n${(this.playTime)} ⏱️`;
            if(this.isQuickRun){
                const link = `https://wikispeedruns.com/play/quick_play?prompt_start=${this.startArticle}&prompt_end=${this.endArticle}${this.language ? '&lang=' + this.language : ''}`;
                resultText += `\n${link}`;
            } else if (this.isSprint) {
                const link = `https://wikispeedruns.com/play/${this.promptId}`;
                resultText += `\n${link}`;
            }
            return resultText;
        },

        generatePath: function(event) {
            return String(this.path);
        },

        //redirect to the corresponding prompt page
        goToLobbyLeaderboard: function (event) {
            window.location.replace(`/lobby/${this.lobbyId}/leaderboard/${this.promptId}?run_id=${this.runId}`);
        },

        goToLeaderboard: function (event) {
            window.location.replace(`/leaderboard/${this.promptId}?run_id=${this.runId}`);
        },
    }
})

