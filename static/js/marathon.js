//JS module imports
import { serverData } from "./modules/serverData.js";
import { getArticleSummary } from "./modules/wikipediaAPI/util.js";
import { submitRun, saveRun, loadRun, removeSave } from "./modules/game/marathon/runs.js";

import { CountdownTimer } from "./modules/game/marathon/countdown.js";
import { MarathonHelp } from "./modules/game/marathon/help.js";
import { FinishPage } from "./modules/game/marathon/finish.js";
import { ArticleRenderer } from "./modules/game/articleRenderer.js";
import { PagePreview } from "./modules/game/pagePreview.js";

import { basicCannon, fireworks, side } from "./modules/confetti.js";

import { submitLocalRun } from "./modules/localStorage/localStorageMarathon.js";

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
        'page-preview': PagePreview
    },
    data: {
        loggedIn: false,
        username: serverData["username"],

        checkpoints: [],
        activeCheckpoints: [],
        visitedCheckpoints: [],
        clicksRemaining: 11,

        startArticle: "",    //For all game modes, this is the first article to load
        lastArticle: "",
        currentArticle: "",
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
        previewContent: null,

        eventTimestamp: null,
        eventType: null,
        eventX: 0,
        eventY: 0
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
        this.loggedIn = "username" in serverData;
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

            console.log(loadedSave)

            this.lastArticle = loadedSave.path[loadedSave.path.length-1];
            this.activeCheckpoints = loadedSave.active_checkpoints;
            this.checkpoints = loadedSave.remaining_checkpoints;
            this.clicksRemaining = loadedSave.clicks_remaining + 1;
            this.lastTime = loadedSave.time;
            this.path = loadedSave.path;
            this.currentArticle = this.path.pop();
            this.visitedCheckpoints = loadedSave.visited_checkpoints;

            if (this.checkpointMarkReached) {
                this.reachedstop = true;
            }

            removeSave(PROMPT_ID)

        } else {

            this.activeCheckpoints = JSON.parse(prompt['initcheckpoints']);
            this.checkpoints = JSON.parse(prompt['checkpoints']);
            this.currentArticle = this.startArticle;
        }

        this.startArticle = prompt['start'];
        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback, this.showPreview, this.hidePreview);
    },


    methods : {

        pageCallback: function(page, loadTime) {

            this.hidePreview();

            if (this.path.length == 0 || this.path[this.path.length - 1] != page) {
                this.path.push(page);
                this.clicksRemaining -= 1;
            }
            
            //this.path.push(page);
            this.currentArticle = page;

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
            
            if (hitcheckpoint) {
                let el = this.checkpoints.shift()
                console.log(el)
                this.activeCheckpoints[checkpointindex] = el

                conf();

                if (!this.reachedstop && this.checkpointMarkReached) {
                    this.showStop = true
                    this.reachedstop = true
                }

            } else if (this.clicksRemaining === 0) {
                this.finish(1);
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
            } else {
                await this.renderer.loadPage(this.startArticle);
            }

            this.started = true;

            setConf();

        },

        async saveRun() {
            this.finished = true;
            this.saved = true;
            // Disable popup
            window.onbeforeunload = null;
            this.endTime = Date.now();

            this.runId = await saveRun(this.$data);
        },

        async finish(finished) {
            if (finished === 0) {
                this.forfeited = true;
            } else {
                side();
            }
            fireworks();

            this.finished = true;
            // Disable popup
            window.onbeforeunload = null;
            this.endTime = Date.now();

            this.runId = await submitRun(this.promptId, this.endTime - this.startTime + this.lastTime, this.visitedCheckpoints, this.path, finished);
            if (!this.loggedIn) {
                submitLocalRun(this.runId, this.promptId, this.endTime - this.startTime + this.lastTime, this.visitedCheckpoints, this.path, finished);
            }

            removeSave(PROMPT_ID);
        
        },

        showPreview: function(e) {
            this.eventTimestamp = e.timeStamp;
            this.eventType = e.type;
            this.eventX = e.clientX;
            this.eventY = e.clientY;
            const href = e.currentTarget.getAttribute("href");
            const title = href.split('/wiki/').pop();
            const promises = [ getArticleSummary(title) ];
            if (e.type !== "click") {
                promises.push(new Promise(resolve => setTimeout(resolve, 600)));
            }
            // const promise1 = getArticleSummary(title);
            // const promise2 = new Promise(resolve => setTimeout(resolve, 500));
            Promise.all(promises).then((values) => {
                if (e.timeStamp === this.eventTimestamp) {
                    this.previewContent = values[0];
                }
            });
        },

        hidePreview: function() {
            this.eventTimestamp = null;
            this.previewContent = null;
        }

    }
});

function setConf() {
    var el = document.getElementById('confettiCanvas')
    el.style.width = window.innerWidth
    el.style.height = window.innerHeight
}

function conf() {
    var myConfetti = confetti.create(document.getElementById('confettiCanvas'), { resize: true
    });
    myConfetti({
        particleCount: 100,
        spread: 90, 
        startVelocity: 40, 
        ticks: 70, 
        zIndex: 9999999, 
        angle: 315,
        origin: { x: 0, y: 0 } , 
    });
    myConfetti({
        particleCount: 100,
        spread: 90, 
        startVelocity: 40, 
        ticks: 70, 
        zIndex: 9999999, 
        angle: 225,
        origin: { x: 1, y: 0 } , 
    });
    myConfetti({
        particleCount: 100,
        spread: 90, 
        startVelocity: 40, 
        ticks: 70, 
        zIndex: 9999999, 
        angle: 45,
        origin: { x: 0, y: 1 } , 
    });
    myConfetti({
        particleCount: 100,
        spread: 90, 
        startVelocity: 40, 
        ticks: 70, 
        zIndex: 9999999, 
        angle: 135,
        origin: { x: 1, y: 1 } , 
    });

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

