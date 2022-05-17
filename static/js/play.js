/* play.js is core of processing gameplay. This includes everything from retrieving information about a prompt,
countdown to start, loading of each wikipedia page, parsing and filtering wikipedia links, processing game logic,
and submitting runs.

With the new Marathon game mode, many of these components are being reused with different game logic. So many of
these components should be as modular/generic as possible.
*/

//JS module imports
import { serverData } from "./modules/serverData.js";
import { startRun, submitRun } from "./modules/game/runs.js";

import { CountdownTimer } from "./modules/game/countdown.js";
import { ArticleRenderer } from "./modules/game/articleRenderer.js";
import { PagePreview } from "./modules/game/pagePreview.js";

import { startLocalRun, submitLocalRun } from "./modules/localStorage/localStorageSprint.js";

// retrieve the unique prompt_id of the prompt to load
const PROMPT_ID = serverData["prompt_id"] || null;

// Get lobby if a lobby_prompt
const LOBBY_ID = serverData["lobby_id"] || null;

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
        'countdown-timer': CountdownTimer,
        'page-preview': PagePreview
    },
    data: {
        startArticle: "",    // For all game modes, this is the first article to load
        endArticle: "",      // For sprint games. Reaching this article will trigger game finishing sequence
        currentArticle: "",
        path: [],             // List of objects to store granular run data, submitted on exit/finish
        /* path object format:
        {
            "article": string,
            "timeReached": number,
            "loadTime": number
        }
        */

        promptId: null,        //Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display
        promptRated: false,
        promptPlayed: false,
        promptActive: false,

        lobbyId: null,
        runId: -1,          //unique ID for the current run. This gets populated upon start of run

        startTime: null,     // The start time of run (ms elapsed since January 1, 1970)
        endTime: null,       // The end time of run (ms elapsed since January 1, 1970)
        elapsed: 0,
        timerInterval: null,
        totalLoadTime: 0,    // Cumulative load time in seconds

        finished: false,     // Flag for whether a game has finished, used for rendering
        started: false,      // Flag for whether a game has started (countdown finished), used for rendering

        loggedIn: false,
    },

    mounted: async function() {
        // Prevent accidental leaves
        window.onbeforeunload = () => true;

        this.loggedIn = "username" in serverData;

        this.promptId = PROMPT_ID;
        this.lobbyId = LOBBY_ID;

        const prompt = await getPrompt(PROMPT_ID, LOBBY_ID);

        this.startArticle = prompt["start"];
        this.endArticle = prompt["end"];

        // !! forces bool if played is not a field
        this.promptPlayed = !!prompt["played"];
        this.promptActive = !!prompt["active"];
        this.promptRated = !!prompt["rated"];

        this.currentArticle = this.startArticle;

        this.runId = await startRun(PROMPT_ID, LOBBY_ID);
        if (!this.loggedIn && this.lobbyId == null) {
            startLocalRun(PROMPT_ID, this.runId);
            console.log("Not logged in, uploading start of run to local storage")
        }

        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback, this.showPreview, this.hidePreview);
        await this.renderer.loadPage(this.startArticle);


        // Update run info on exit/page hide
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "hidden") {
                this.updateRun();
            }
        });

        // Use pagehide for browsers that don't support visibilitychange
        if ("onpagehide" in self) {
            document.addEventListener("pagehide", this.updateRun, {capture: true});
        } else {
            // Only register beforeunload/unload for browsers that don't support pagehide
            // Avoids breaking bfcache
            document.addEventListener("unload", this.updateRun, {capture: true});
            document.addEventListener("beforeunload", this.updateRun, {capture: true});
        }
    },


    methods : {
        updateRun: function() {
            if (!this.finished) {
                this.endTime = Date.now();
            }

            submitRun(PROMPT_ID, LOBBY_ID, this.runId, this.startTime, this.endTime, this.finished, this.path);
        },

        pageCallback: function(page, loadTime) {

            this.hidePreview();
            // Game logic for sprint mode:

            let loadTimeSeconds = loadTime / 1000;

            if (this.path.length == 0 || this.path[this.path.length - 1]["article"] != page) {
                // Update path
                let timeElapsed = (Date.now() - this.startTime) / 1000;
                this.path.push({
                    "article": page,
                    "timeReached": timeElapsed,
                    "loadTime": loadTimeSeconds
                });

                // Update partial run information
                this.updateRun();
            }

            this.currentArticle = page;
            this.totalLoadTime += loadTimeSeconds;

            //if the page's title matches that of the end article, finish the game, and submit the run
            if (page === this.endArticle) {
                this.finish();
            }

        },

        async start() {
            // start timer
            this.startTime = Date.now();

            // set the timer update interval
            this.timerInterval = setInterval(() => {
                const seconds = (Date.now() - this.startTime) / 1000;
                this.elapsed = seconds - this.totalLoadTime;
            }, 50);


            this.started = true;
        },

        async finish() {
            this.finished = true;
            // Disable popup
            window.onbeforeunload = null;

            this.endTime = Date.now();

            this.runId = await submitRun(PROMPT_ID, LOBBY_ID, this.runId, this.startTime, this.endTime, this.finished, this.path);
            if (!this.loggedIn && this.lobbyId == null) {
                submitLocalRun(PROMPT_ID, this.runId, this.startTime, this.endTime, this.finished, this.path);
                console.log("Not logged in, submitting run to local storage")
                //console.log(this.runId)
            }

            //fireworks();
            if (this.lobbyId == null) {
                window.location.replace(`/finish?run_id=${this.runId}&played=true`);
            } else {
                window.location.replace(`/lobby/${this.lobbyId}/finish?run_id=${this.runId}&played=true`);
            }

        },

        showPreview: function(e) {
            this.$refs.pagePreview.showPreview(e);
        },

        hidePreview: function(e) {
            this.$refs.pagePreview.hidePreview(e);
        },

    }
})


// Disable find hotkeys, players will be given a warning
window.addEventListener("keydown", function(e) {
    //disable find
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) {
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
});
