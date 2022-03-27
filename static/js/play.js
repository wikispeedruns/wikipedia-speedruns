/* play.js is core of processing gameplay. This includes everything from retrieving information about a prompt,
countdown to start, loading of each wikipedia page, parsing and filtering wikipedia links, processing game logic,
and submitting runs.

With the new Marathon game mode, many of these components are being reused with different game logic. So many of
these components should be as modular/generic as possible.
*/

//JS module imports
import { serverData } from "./modules/serverData.js";
import { fetchJson } from "./modules/fetch.js";
import { startRun, submitRun } from "./modules/game/runs.js";
import { getArticleSummary } from "./modules/wikipediaAPI/util.js";

import { CountdownTimer } from "./modules/game/countdown.js";
import { FinishPage } from "./modules/game/finish.js";
import { ArticleRenderer } from "./modules/game/articleRenderer.js";

import { basicCannon, fireworks, side } from "./modules/confetti.js";

import { startLocalRun, submitLocalRun } from "./modules/localStorage/localStorageSprint.js";


// retrieve the unique prompt_id of the prompt to load
const PROMPT_ID = serverData["prompt_id"];

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
        'finish-page': FinishPage
    },
    data: {
        startArticle: "",    //For all game modes, this is the first article to load
        endArticle: "",      //For sprint games. Reaching this article will trigger game finishing sequence
        currentArticle: "",
        articlePreview: "",
        path: [],             //array to store the user's current path so far, submitted with run

        promptId: null,        //Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display
        lobbyId: null,
        runId: -1,          //unique ID for the current run. This gets populated upon start of run

        startTime: null,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        elapsed: 0,
        timerInterval: null,

        finished: false,     //Flag for whether a game has finished, used for rendering
        started: false,      //Flag for whether a game has started (countdown finished), used for rendering

        renderer: null,
        loggedIn: false,
        hover: false,
        loading: false,

        clientX: 0,
        clientY: 0
    },

    mounted: async function() {

        this.loggedIn = "username" in serverData;

        this.promptId = PROMPT_ID;
        this.lobbyId = LOBBY_ID;

        const prompt = await getPrompt(PROMPT_ID, LOBBY_ID);

        this.startArticle = prompt["start"];
        this.endArticle = prompt["end"];

        this.currentArticle = this.startArticle;

        if (this.loggedIn || this.lobbyId != null) {
            this.runId = await startRun(PROMPT_ID, LOBBY_ID);
        } else {
            this.runId = startLocalRun(PROMPT_ID);
            console.log("Not logged in, adding to local storage")
            //console.log(this.runId);
        }

        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback, this.setupPreviews);
    },


    methods : {
        async pageCallback(page, loadTime) {

            // console.log("page callback")

            this.loading = false;
            this.hover = false;
            // Game logic for sprint mode:

            if (this.path.length == 0 || this.path[this.path.length - 1] != page) {
                this.path.push(page);
            }
            //this.path.push(page);

            this.currentArticle = page;

            this.startTime += loadTime;

            setMargin();

            //if the page's title matches that of the end article, finish the game, and submit the run
            if (page.replace("_", " ").toLowerCase() === this.endArticle.replace("_", " ").toLowerCase()) {

                this.finished = true;

                // Disable popup
                window.onbeforeunload = null;

                this.endTime = Date.now();

                if (this.loggedIn || this.lobbyId != null) {
                    this.runId = await submitRun(PROMPT_ID, LOBBY_ID, this.runId, this.startTime, this.endTime, this.path);
                } else {
                    this.runId = submitLocalRun(PROMPT_ID, this.runId, this.startTime, this.endTime, this.path);
                    console.log("Not logged in, submitting run to local storage")
                }

                fireworks();
            }

        },

        async start() {
            //Toggle the `started` render flag, which will hide all other elements, and display the rendered wikipage
            this.started = true;
            //start timer
            this.startTime = Date.now();

            //set the timer update interval
            this.timerInterval = setInterval(() => {
                const seconds = (Date.now() - this.startTime) / 1000;
                this.elapsed = seconds;
            }, 50);

            await this.renderer.loadPage(this.startArticle);

            this.setupPreviews();
            await this.pageCallback(this.startArticle, Date.now() - this.startTime)
        },

        displayPreview: function() {
            let html = "";
            if ("originalimage" in this.articlePreview) {
                html += '<img src="' + this.articlePreview["originalimage"]["source"] + '"/>';
            }
            html += '<div>' + this.articlePreview["extract_html"] + '</div>';
            return html;
        },

        computePosition: function() {
            const vh = window.innerHeight;
            const vw = window.innerWidth;
            const styleObject = new Object();
            if (this.clientX < vw / 2.0) {
                styleObject['left'] = `${this.clientX+10}px`;
            } else {
                styleObject['right'] = `${vw-this.clientX+10}px`;
            }
            if (this.clientY < vh / 2.0) {
                styleObject['top'] = `${this.clientY+10}px`;
            } else {
                styleObject['bottom'] = `${vh-this.clientY+10}px`;
            }
            return styleObject;
        },

        mouseEnter: function(e) {
            this.loading = true;
            const href = e.currentTarget.getAttribute("href");
            const title = href.split('/wiki/').pop();
            // const promise1 = getArticleSummary(title);
            // const promise2 = new Promise(resolve => setTimeout(resolve, 500));
            getArticleSummary(title).then(resp => {
                if (this.loading) {
                    this.articlePreview = resp;
                    this.hover = true;
                    this.clientX = e.clientX;
                    this.clientY = e.clientY;
                }
            });
        },

        mouseLeave: function() {
            this.loading = false;
            this.hover = false;
            this.articlePreview = '';
        },

        setupPreviews: function() {
            document.getElementById("wikipedia-frame").querySelectorAll("a").forEach(e => {
                if (e.hasAttribute("href") && e.getAttribute("href").startsWith("/wiki/")) {
                    e.addEventListener("mouseenter", this.mouseEnter);
                    e.addEventListener("mouseleave", this.mouseLeave);
                }
            });
        }

    }
})

function setMargin() {
    const element = document.getElementById("time-box");
    let margin = (element.offsetHeight + 25) > 100 ? (element.offsetHeight + 25) : 100
    document.getElementById("wikipedia-frame").style.marginBottom = margin +"px";
}

// Prevent accidental leaves
window.onbeforeunload = function() {
    return true;
};

// Disable find hotkeys, players will be given a warning
window.addEventListener("keydown", function(e) {
    //disable find
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) {
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
});
