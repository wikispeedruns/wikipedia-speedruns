/* play.js is core of processing gameplay. This includes everything from retrieving information about a prompt,
countdown to start, loading of each wikipedia page, parsing and filtering wikipedia links, processing game logic,
and submitting runs.

With the new Marathon game mode, many of these components are being reused with different game logic. So many of
these components should be as modular/generic as possible.
*/

//JS module imports
import { serverData } from "./modules/serverData.js";

import { getRandTip } from "./modules/game/tips.js";
import { startRun, submitRun } from "./modules/game/runs.js";

import { CountdownTimer } from "./modules/game/countdown.js";
import { FinishPage } from "./modules/game/finish.js";
import { ArticleRenderer } from "./modules/game/articleRenderer.js";

import { basicCannon, fireworks, side } from "./modules/confetti.js";


//retrieve the unique prompt_id of the prompt to load
const PROMPT_ID = serverData["prompt_id"];

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
        path: [],             //array to store the user's current path so far, submitted with run

        promptId: 0,        //Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display
        runId: -1,          //unique ID for the current run. This gets populated upon start of run

        startTime: null,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        elapsed: 0,
        timerInterval: null,

        finished: false,     //Flag for whether a game has finished, used for rendering
        started: false,      //Flag for whether a game has started (countdown finished), used for rendering

        renderer: null,
    },


    mounted: async function() {
        this.promptId = PROMPT_ID;

        const response = await fetch("/api/sprints/" + this.promptId);
        if (response.status != 200) {
            const error = await response.text();
            this.alert(error);

            // Prevent are you sure you want to leave prompt
            window.onbeforeunload = null;
            window.location.replace("/");   // TODO error page

            return;
        }
        const prompt = await response.json();

        this.startArticle = prompt["start"];
        this.endArticle = prompt["end"];

        this.runId = await startRun(this.promptId);

        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback);
    },


    methods : {
        async pageCallback(page, loadTime) {
            // Game logic for sprint mode:
            this.path.push(page);

            this.startTime += loadTime;

            //if the page's title matches that of the end article, finish the game, and submit the run
            if (page.replace("_", " ").toLowerCase() === this.endArticle.replace("_", " ").toLowerCase()) {

                this.finished = true;

                // Disable popup
                window.onbeforeunload = null;

                this.endTime = Date.now();
                await submitRun(this.runId, this.startTime, this.endTime, this.path);

                fireworks();
            }

        },

        async start() {
            await this.renderer.loadPage(this.startArticle);

            this.path.push(this.startArticle);

            //once above conditions are met, toggle the `started` render flag, which will hide all other elements, and display the rendered wikipage
            this.started = true;

            //start timer
            this.startTime = Date.now();

            //set the timer update interval
            this.timerInterval = setInterval(() => {
                const seconds = (Date.now() - this.startTime) / 1000;
                this.elapsed = seconds;
            }, 50);
        },

    }
})

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
