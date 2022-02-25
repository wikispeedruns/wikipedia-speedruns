/* play.js is core of processing gameplay. This includes everything from retrieving information about a prompt,
countdown to start, loading of each wikipedia page, parsing and filtering wikipedia links, processing game logic,
and submitting runs.

With the new Marathon game mode, many of these components are being reused with different game logic. So many of
these components should be as modular/generic as possible.
*/

//JS module imports
import { serverData } from "./modules/serverData.js";
import { playGame } from "./modules/playmodule.js";
import { getRandTip } from "./modules/game/tips.js";

import { CountdownTimer } from "./modules/game/countdown.js";

//retrieve the unique prompt_id of the prompt to load
const prompt_id = serverData["prompt_id"];

//Vue container. This contains data, rendering flags, and functions tied to game logic and rendering. See play.html
let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'countdown-timer': CountdownTimer
    },
    data: {
        gameType: "sprint",  //'sprint' or 'marathon'
        startArticle: "",    //For all game modes, this is the first article to load
        endArticle: "",      //For sprint games. Reaching this article will trigger game finishing sequence
        prompt_id: 0,        //Unique prompt id to load, this should be identical to 'const prompt_id', but is mostly used for display
        run_id: -1,          //unique ID for the current run. This gets populated upon start of run
        path:[],             //array to store the user's current path so far, submitted with run
        timer: "",           //string for displaying of the timer in seconds.
        countdown: 8,        //The countdown duration in seconds
        startTime: null,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        finalTime:"",        //For all game modes, total runtime, only used for rendering.
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        finished: false,     //Flag for whether a game has finished, used for rendering
        started: false,      //Flag for whether a game has started (countdown finished), used for rendering
        activeTip: "",       //variable used to store the game tip displayed on the countdown screen
    },

    methods : {
        //redirect to the corresponding prompt page
        finishPrompt: function (event) {
            window.location.replace("/prompt/" + this.prompt_id + "?run_id=" + this.run_id);
        },

        //go back to home page
        home: function (event) {
            window.location.replace("/");
        },

        //copy sharable result
        copyResults: function(event) {
            let results = this.generateResults();
            document.getElementById("custom-tooltip").style.display = "inline";
            navigator.clipboard.writeText(results);
            setTimeout(function() {
                document.getElementById("custom-tooltip").style.display = "none";
            }, 1500);
        },

        generateResults: function(event) {
            if (this.gameType === "sprint") {
                return `Wiki Speedruns ${this.prompt_id}
                ${this.startArticle}
                ${this.path.length - 1} 🖱️
                ${(this.endTime - this.startTime) / 1000} ⏱️`
            } else {
                return "";
            }
        },

        checkFinishingCondition: function(title) {
            return title.replace("_", " ").toLowerCase() === this.endArticle.replace("_", " ").toLowerCase()
        },


        startRun() {
            playGame(this)
        },


        async submitRun() {
            const reqBody = {
                "start_time": this.startTime,
                "end_time": this.endTime,
                "path": this.path,
            }

            // Send results to API
            try {
                const response = await fetch(`/api/runs/${this.run_id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(reqBody)
                })

            } catch(e) {
                console.log(e);
            }
        }
    }
})


//send request to create an empty run, returns the run_id
async function saveEmptyRun() {
    const reqBody = {
        "prompt_id": prompt_id,
    }
    try {
        const response = await fetch("/api/runs", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })
        return await response.json();
    } catch(e) {
        console.log(e);
    }
}

//Upon load
window.addEventListener("load", async function() {
    //get prompt information
    const response = await fetch("/api/sprints/" + prompt_id);
    if (response.status != 200) {
        const error = await response.text();
        this.alert(error)
        // Prevent are your sure you want to leave prompt
        window.onbeforeunload = null;
        window.location.replace("/");   // TODO error page
        return;

    }

    const prompt = await response.json();

    //check if the retrieved prompt is available to play. If not, redirect user to home
    if (!prompt['available']) {
        this.alert("This prompt is not yet available! Redirecting back to home");
        window.onbeforeunload = null;
        window.location.replace("/");
        return;
    }

    //populate vue data
    app.$data.prompt_id = prompt_id;
    app.$data.startArticle = prompt["start"];
    app.$data.endArticle = prompt["end"];
    app.$data.run_id = await saveEmptyRun(); // Save run on clicking "play" when `prompt_id` is valid
    app.$data.activeTip = getRandTip();
});

//prevent accidental leaves
window.onbeforeunload = function() {
    return true;
};

//Disable find hotkeys, players will be given a warning
window.addEventListener("keydown", function(e) {
    //disable find
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) {
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
});
