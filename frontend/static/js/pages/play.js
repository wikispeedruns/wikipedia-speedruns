/* play.js is core of processing gameplay. This includes everything from retrieving information about a prompt,
countdown to start, loading of each wikipedia page, parsing and filtering wikipedia links, processing game logic,
and submitting runs.

With the new Marathon game mode, many of these components are being reused with different game logic. So many of
these components should be as modular/generic as possible.
*/

//JS module imports
import Vue from "vue/dist/vue.esm.js";

import { startRun, submitRun } from "../modules/game/runs.js";


import { WaitForHost } from "../modules/game/waitForHost.js";

import { CountdownTimer } from "../modules/game/countdown.js";
import { ArticleRenderer } from "../modules/game/articleRenderer.js";
import { PagePreview } from "../modules/game/pagePreview.js";

import { startLocalRun, submitLocalRun } from "../modules/localStorage/localStorageSprint.js";

import { triggerLeaderboardUpdate } from "../modules/live/liveLeaderboard.js";
import { getArticleTitle } from "../modules/wikipediaAPI/util.js";


// retrieve the unique prompt_id of the prompt to load
const PROMPT_ID = serverData["prompt_id"] || null;

// Or get the prompt for a quick run
const PROMPT_START = serverData["prompt_start"] || null;
const PROMPT_END = serverData["prompt_end"] || null;

// Get lobby if a lobby_prompt
const LOBBY_ID = serverData["lobby_id"] || null;

const USERNAME = serverData["username"] || null;
const LOBBY_NAME = serverData["lobby_name"] || null;

// Get if auto scroll is on
const IS_SCROLL_ON = serverData["scroll"] || null;

// Get language
const LANGUAGE = serverData["lang"];

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

async function getPrompt(promptId, lobbyId=null) {

    if(promptId == null){
        return {start: PROMPT_START, end: PROMPT_END, language: LANGUAGE};
    }

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
        'wait-for-host': WaitForHost,
        'page-preview': PagePreview
    },
    data: {
        startArticle: "",    // For all game modes, this is the first article to load
        endArticle: "",      // For sprint games. Reaching this article will trigger game finishing sequence
        endArticleResolved: "", // End article title after redirect resolution
        currentArticle: "",
        language: "",
        path: [],             // List of objects to store granular run data, submitted on exit/finish
        /* path object format:
        {
            "article": string,
            "timeReached": number,
            "loadTime": number,
            "penaltyTime": number
        }
        */

        promptId: null,        // Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display
        revisionDate: null,

        lobbyId: null,
        runId: -1,          //unique ID for the current run. This gets populated upon start of ru

        startTime: Date.now(),     // The start time of run (ms elapsed since January 1, 1970)
        endTime: null,       // The end time of run (ms elapsed since January 1, 1970)
        countdownTime: 0,  // Time spent in countdown screen (seconds)

        elapsed: 0,             // Total time elapsed in ms (frontend)
        timerInterval: null,

        offset: Date.now(),           // Offset time since last pause, initially approx. startTime
        isRunning: false,       // Whether the timer is running
        milliseconds: 0,        // Current ms since last pause (frontend)
        savedMilliseconds: 0,   // Cumulative pause times (frontend)

        finished: false,     // Flag for whether a game has finished, used for rendering
        started: false,      // Flag for whether a game has started (countdown finished), used for rendering

        loggedIn: false,

        expandedTimebox: true,
        isMobile: false,

        isScroll: null,

        isPenaltyMode: false,
        isFindHotkeyMode: false,
        penaltyTime: 0,         // Additional penalty time for penalty game mode

        // State for live games. We need to access the username/lobby name 
        live: false,
        isHost: false,
        username: USERNAME,
        lobbyName: LOBBY_NAME
    },

    mounted: async function() {
        // Prevent accidental leaves
        this.isMobile = window.screen.width < 768;

        window.onbeforeunload = () => true;

        this.loggedIn = "username" in serverData;

        this.promptId = PROMPT_ID;
        this.lobbyId = LOBBY_ID;
        this.isScroll = IS_SCROLL_ON;

        const prompt = await getPrompt(PROMPT_ID, LOBBY_ID);

        this.isPenaltyMode = false;
        this.isFindHotkeyMode = false;
        if (LOBBY_ID != null) {
            const lobby = await getLobby(LOBBY_ID);
            this.isPenaltyMode = !!lobby["rules"]["is_penalty_mode"];
            this.live = !!lobby?.["rules"]?.["live_mode"];
            this.isFindHotkeyMode = !!lobby?.["rules"]?.["find_hotkey_mode"];
            this.isHost = lobby?.["user"]?.["owner"];
        }

        this.startArticle = prompt["start"];
        this.endArticle = prompt["end"];
        this.language = prompt["language"] || LANGUAGE || "en";
        this.resolveArticleTitle(this.endArticle).then((resolvedTitle) => {
            this.endArticleResolved = resolvedTitle || "";
        });

        // !! forces bool if played is not a field
        this.promptPlayed = !!prompt["played"];
        this.promptActive = !!prompt["active"];
        this.promptRated = !!prompt["rated"];

        // Use the release date of teh prompt (if it exists) to determine the article revision
        this.revisionDate = prompt?.["active_start"];
        this.currentArticle = this.startArticle;

        this.runId = await startRun(PROMPT_ID, LOBBY_ID, PROMPT_START, PROMPT_END, LANGUAGE);
        if (!this.loggedIn && this.lobbyId == null) {
            startLocalRun(PROMPT_ID, PROMPT_START, PROMPT_END, this.runId, LANGUAGE);
            console.log("Not logged in, uploading start of run to local storage")
        }


        this.offset = this.startTime;

        this.renderer = new ArticleRenderer(
            document.getElementById("wikipedia-frame"),
            this.pageCallback,
            !this.isScroll && this.showPreview,
            !this.isScroll && this.hidePreview,
            this.loadCallback,
            this.language,
            this.revisionDate);
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

        // Start listening for hotkeys (to check for find in page hotkeys)
        window.addEventListener("keydown", this.keydownHandler);
    },

    beforeUnmount: function() {
        window.removeEventListener("keydown", this.keydownHandler);
    },

    methods : {
        resolveArticleTitle: async function(title) {
            if (!title) return null;
            const lang = this.language || LANGUAGE || "en";
            try {
                return await getArticleTitle(title, lang);
            } catch (error) {
                console.warn("Failed to resolve article title:", title, error);
                return null;
            }
        },

        updateRun: function() {
            if (!this.finished) {
                this.endTime = Date.now();
            }

            submitRun(PROMPT_ID, LOBBY_ID, this.runId, this.startTime, this.endTime, this.finished, this.path);
        },

        loadCallback: function() {
            this.stopTimer();
        },

        pageCallback: function(page, loadTime) {
            window.scrollTo(0, 0);
            this.hidePreview();
            if (this.isScroll) {
                document.getElementById("wikipedia-frame").scrollTo(0, 0);
            }
            this.startTimer();

            let loadTimeSeconds = loadTime / 1000;
            this.currentArticle = page;

            if (this.live) {
                triggerLeaderboardUpdate(this.lobbyId, this.promptId);
            }

            if (this.path.length == 0 || this.path[this.path.length - 1]["article"] != page) {
                // Update path
                let timeElapsed = (Date.now() - this.startTime) / 1000;
		
		        if (this.isPenaltyMode) {
                    this.penaltyTime = (this.path.length) * 20;
		        }
		
                this.path.push({
                    "article": page,
                    "timeReached": timeElapsed,
                    "loadTime": loadTimeSeconds,
                    "penaltyTime": this.penaltyTime
                });

                // Set first page timeReached if first page loaded after start() is called
                if (this.path.length == 1 && this.started) {
                    this.path[0]['timeReached'] = this.countdownTime;
                }

                // Finish if we match the resolved goal (backup is original end), otherwise update partial run info
                const goalArticle = this.endArticleResolved || this.endArticle;
                if (page === goalArticle) {
                    this.finish();
                } else {
                    this.updateRun();
                }
            }

        },

        async start() {
            this.countdownTime = (Date.now() - this.startTime) / 1000;

            // Set first page timeReached if start() called after first page is loaded
            if (this.path.length == 1) {
                this.path[0]['timeReached'] = this.countdownTime;
            }

            this.resetTimer();
            this.startTimer();

            this.timerInterval = setInterval(() => {
                if (!this.isRunning) return;

                this.milliseconds = Date.now() - this.offset;
	    	    if (this.isPenaltyMode) {
		            this.milliseconds += 20000;
                    if(this.path.length == 1){
                        this.milliseconds -= 20000;
                    }
                    
	    	    }

                this.elapsed = (this.milliseconds + this.savedMilliseconds) / 1000;


            }, 10);

            if (this.isScroll) {
                setInterval(function() {
                    const elem = document.getElementById("wikipedia-frame");
                    elem.scrollBy(0, 1);
                    if (Math.abs(elem.scrollHeight - elem.clientHeight - elem.scrollTop) < 1) {
                        elem.scrollTo(0, 0);
                    }
                }, 20);
            }

            this.started = true;

            // This is not ideal, we want to scroll users to top upon start
            // 100ms is human reaction time, so I think this should be fine lol
            setTimeout(() => {
                window.scrollTo(0, 0)
            }, 100);
        },

        async finish() {
            this.finished = true;
            // Disable popup
            window.onbeforeunload = null;

            this.endTime = Date.now();

            this.runId = await submitRun(PROMPT_ID, LOBBY_ID, this.runId, this.startTime, this.endTime, this.finished, this.path);
            if (!this.loggedIn && this.lobbyId == null) {
                submitLocalRun(PROMPT_ID, PROMPT_START, PROMPT_END, this.runId, this.startTime, this.endTime, this.finished, this.path, LANGUAGE);
                console.log("Not logged in, submitting run to local storage");
                //console.log(this.runId)
            }

            triggerLeaderboardUpdate(this.lobbyId, this.promptId);

            if (this.promptId == null){
                window.location.replace(`/quick_run/finish?run_id=${this.runId}&played=true`)
            }
            else if (this.lobbyId == null) {
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

        startTimer() {
            if (this.isRunning) return;

            this.isRunning = true;
            this.offset = Date.now();
        },

        stopTimer() {
            this.savedMilliseconds += this.milliseconds;
            this.milliseconds = 0;
            this.isRunning = false;
        },

        resetTimer() {
            this.milliseconds = 0;
            this.savedMilliseconds = 0;
            this.offset = Date.now();
        },

        giveUp: function (event) {
            window.onbeforeunload = null;
            if (this.promptId == null){
                window.location.replace(`/`)
            }
            else if (this.lobbyId == null) {
                window.location.replace(`/leaderboard/${this.promptId}?run_id=${this.runId}`);
            } else {
                window.location.replace(`/lobby/${this.lobbyId}/leaderboard/${this.promptId}?run_id=${this.runId}`);
            }        
        },

        // Prevent find hotkeys unless allowed by the rules
        keydownHandler: function(e) {
            if (this.isFindHotkeyMode) return;
            
            if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && (e.keyCode == 70 || e.keyCode == 71))) {
                e.preventDefault();
                alert("WARNING: Attempt to Find in page. This will be recorded.");
            }
        },
    }
})
