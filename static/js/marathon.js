//JS module imports
import { serverData } from "./modules/serverData.js";

import { submitRun, saveRun, loadRun, removeSave } from "./modules/game/marathon/runs.js";

import { CountdownTimer } from "./modules/game/marathon/countdown.js";
import { MarathonHelp } from "./modules/game/marathon/help.js";
import { FinishPage } from "./modules/game/marathon/finish.js";
import { ArticleRenderer } from "./modules/game/articleRenderer.js";

//retrieve the unique prompt_id of the prompt to load
const PROMPT_ID = serverData["prompt_id"];
const load_save = serverData["load_save"] === '1';

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'countdown-timer': CountdownTimer,
        'finish-page': FinishPage,
        'marathon-help': MarathonHelp,
    },
    data: {

        checkpoints: [],
        activeCheckpoints: [],
        visitedCheckpoints: [],
        clicksRemaining: 11,

        startArticle: "",    //For all game modes, this is the first article to load
        lastArticle: "",
        path: [],             //array to store the user's current path so far, submitted with run

        promptId: 0,        //Unique prompt id to load, this should be identical to 'const PROMPT_ID', but is mostly used for display
        runId: -1,          //unique ID for the current run. This gets populated upon start of run

        startTime: 0,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        lastTime:0,
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        elapsed: 0,
        timerInterval: null,

        numCheckpointsToStop: 10,
        startingNumClicksToAdd: 5,

        finished: false,     //Flag for whether a game has finished, used for rendering
        started: false,      //Flag for whether a game has started (countdown finished), used for rendering
        forfeited: false,
        showHelp: false,
        showStop: false,
        reachedstop: false,  //This variable only gets flipped once, its to prevent the stop box from showing up everytime the page is loaded
        saved: false,

        renderer: null,
    },

    computed: {
        numCheckpointsVisited: function() {
            return this.visitedCheckpoints.length
        },

        numVisitedUnique: function () {
            return new Set(this.path).size;
        },

        clicksPerCheckpoint: function () {
            let projected = this.startingNumClicksToAdd - parseInt(this.numCheckpointsVisited/this.numCheckpointsToStop)
            return Math.max(projected, 2)
        },

        checkpointMarkReached: function () {
            return this.numCheckpointsVisited >= this.numCheckpointsToStop
        },
    },


    mounted: async function() {
        this.promptId = PROMPT_ID;

        const response = await fetch("/api/marathon/prompt/" + this.promptId);
        if (response.status != 200) {
            const error = await response.text();
            this.alert(error);
            // Prevent are you sure you want to leave prompt
            window.onbeforeunload = null;
            window.location.replace("/");   // TODO error page

            return;
        }
        const prompt = await response.json();

        if (load_save) {
            const loadedSave = loadRun(PROMPT_ID)
            this.lastArticle = loadedSave.path[loadedSave.path.length-1]
            this.activeCheckpoints = loadedSave.active_checkpoints
            this.checkpoints = loadedSave.remaining_checkpoints
            this.clicksRemaining = loadedSave.clicks_remaining + 1
            this.lastTime = loadedSave.time
            this.path = loadedSave.path
            this.path.pop()
            this.visitedCheckpoints = loadedSave.visited_checkpoints

            if (this.checkpointMarkReached) {
                this.reachedstop = true
            }

            removeSave(PROMPT_ID)

        } else {

            this.activeCheckpoints = JSON.parse(prompt['initcheckpoints']);
            this.checkpoints = JSON.parse(prompt['checkpoints']);
        }

        this.startArticle = prompt['start'];
        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback);
    },


    methods : {
        async pageCallback(page, loadTime) {

            this.clicksRemaining -= 1;
            
            this.path.push(page);

            this.startTime += loadTime;

            let hitcheckpoint = false;
            let checkpointindex = -1;
            for (let i = 0; i < this.activeCheckpoints.length; i++) {
                if (page.replace("_", " ").toLowerCase() === this.activeCheckpoints[i].replace("_", " ").toLowerCase()) {
                    this.clicksRemaining += this.clicksPerCheckpoint + 1;
                    //query for new checkpoint
                    checkpointindex = i;
                    hitcheckpoint = true;
                    this.visitedCheckpoints.push(page);
                }
            }

            if (this.clicksRemaining === 0) {
                await this.finish(1);
            }

            setMargin();

            if (hitcheckpoint) {
                let got = false
                this.checkpoints.forEach(bucket => {
                    if (bucket.length > 0 && !got) {
                        let el = bucket.pop()
                        console.log(el)
                        this.activeCheckpoints[checkpointindex] = el
                        got = true
                    }
                })
            }

            if (!this.reachedstop && this.checkpointMarkReached) {
                this.showStop = true
                this.reachedstop = !this.reachedstop
            }
        },

        async start() {
            //start timer
            this.startTime = Date.now();

            //set the timer update interval
            this.timerInterval = setInterval(() => {
                const seconds = (Date.now() - this.startTime + this.lastTime) / 1000;
                this.elapsed = seconds;
            }, 50);

            if (load_save) {
                await this.renderer.loadPage(this.lastArticle);
                await this.pageCallback(this.lastArticle, Date.now() - this.startTime)
            } else {
                await this.renderer.loadPage(this.startArticle);
                await this.pageCallback(this.startArticle, Date.now() - this.startTime)
            }

            this.started = true;

            setMargin();

        },

        async saveRun() {
            this.finished = true;
            this.saved = true;
            // Disable popup
            window.onbeforeunload = null;
            this.endTime = Date.now() + this.lastTime;

            this.runId = await saveRun(this.$data);
        },

        async finish(finished) {
            if (finished === 0) {
                this.forfeited = true;
            }

            this.finished = true;
            // Disable popup
            window.onbeforeunload = null;
            this.endTime = Date.now();

            this.runId = await submitRun(this.promptId, this.endTime - this.startTime, this.visitedCheckpoints, this.path, finished);
            removeSave(PROMPT_ID)
        },

        formatActiveCheckpoints: function() {
            let output = ""
            for (let i = 0; i < this.activeCheckpoints.length - 1; i++) {
                output += String(i+1) + ": <strong>"
                output += this.activeCheckpoints[i]
                output += "</strong><br>"
            }
            output += String(this.activeCheckpoints.length) + ": <strong>"
            output += this.activeCheckpoints[this.activeCheckpoints.length - 1]
            output += "</strong>"

            return output
        },

    }
});

function setMargin() {
    const element = document.getElementById("time-box");
    let margin = (element.offsetHeight + 25) > 250 ? (element.offsetHeight + 25) : 250
    document.getElementById("wikipedia-frame").lastChild.style.paddingBottom = margin +"px";
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

