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
        timer: "",
        countdown: 8,
        finished: false,
        started: false,
        activeTip: "",
        path:[],
        finalTime:"",
        endTime: null,
        prompt_id: 0,
        run_id: -1,
        startTime: null,
    },
    methods : {
        formatPath: function (pathArr) {
            let output = "";
            for(let i=0; i<pathArr.length - 1;i++) {
                output = output.concat(pathArr[i])
                output = output.concat(" -> ")
            }
            output = output.concat(pathArr[pathArr.length - 1])
            return output;
        }, 

        finishPrompt: function (event) {
            window.location.replace("/prompt/" + this.prompt_id + "?run_id=" + this.run_id);
        }, 

        home: function (event) {
            window.location.replace("/");
        },

        copyResults: function(event) {
            let results = this.generateSprintResults();
            document.getElementById("custom-tooltip").style.display = "inline";
            navigator.clipboard.writeText(results);
            setTimeout(function() {
                document.getElementById("custom-tooltip").style.display = "none";
            }, 1500);
        },

        generateSprintResults: function(event) {
            return `Wiki Speedruns ${this.prompt_id}
            ${this.startArticle}
            ${this.path.length - 1} 🖱️
            ${(this.endTime - this.startTime) / 1000} ⏱️`
        }
    }
})

async function saveRun() {
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
    app.$data.run_id = await saveRun(); // Save run on clicking "play" when `prompt_id` is valid
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
