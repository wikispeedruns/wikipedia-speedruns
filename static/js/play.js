import { serverData } from "./modules/serverData.js";
import { playGame } from "./modules/playmodule.js";
import { getRandTip } from "./modules/tooltips.js";

const prompt_id = serverData["prompt_id"];

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        gameType: "sprint",
        startArticle: "",
        endArticle: "",
        prompt_id: 0,
        run_id: -1,
        path:[],
        timer: "",
        countdown: 8,
        startTime: null,
        finalTime:"",
        endTime: null,
        finished: false,
        started: false,
        activeTip: "",
    },
    methods : {
        finishPrompt: function (event) {
            window.location.replace("/prompt/" + this.prompt_id + "?run_id=" + this.run_id);
        }, 

        home: function (event) {
            window.location.replace("/");
        },

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
        }
    }
})

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


window.addEventListener("load", async function() {
    const response = await fetch("/api/sprints/" + prompt_id);

    if (response.status != 200) {
        const error = await response.text();
        this.alert(error)
        // Prevent are your sure you want to leave prompt
        window.onbeforeunload = null;
        window.location.replace("/");   // TODO error page
    }

    const prompt = await response.json();

    app.$data.prompt_id = prompt_id;
    app.$data.startArticle = prompt["start"];
    app.$data.endArticle = prompt["end"];
    app.$data.run_id = await saveEmptyRun(); // Save run on clicking "play" when `prompt_id` is valid
    app.$data.activeTip = getRandTip();

    playGame(app)
});

window.onbeforeunload = function() {
    return true;
};

window.addEventListener("keydown", function(e) {
    //disable find
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) { 
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
});    
