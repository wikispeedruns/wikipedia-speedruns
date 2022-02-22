import { serverData } from "./modules/serverData.js"

const prompt_id = serverData["prompt_id"];
const run_id = serverData["run_id"] ? serverData["run_id"] : "";
const pg = serverData["pg"];

const runsPerPage = 20;

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        prompt: [],
        runs: [],
        renderedRuns: [],
        currentRun: null,
        currentRunPosition: 0,
        runsPerPage: runsPerPage,
        run_id: run_id,
    },

    methods: {
        getPrompt: async function() {
            var response = await fetch("/api/marathon/prompt/" + prompt_id);
            return await response.json();
        },

        getRuns: async function() {
            var response = await fetch("/api/marathon/prompt/" + prompt_id + "/leaderboard/" + run_id);
            return await response.json();
        },

        getPageNo: function() {
            return parseInt(pg)
        },

        getPromptID: function() {
            return prompt_id;
        },

        getRunID: function() {
            return run_id;
        },

        paginate: function() {
            const first = (pg - 1) * runsPerPage
            const last = pg * runsPerPage
            for (let i = 0; i < this.runs.length; i++) {
                let run = this.runs[i]
                if (run_id) {
                    if (run.run_id === parseInt(run_id)) {
                        this.currentRun = run;
                        if (i < first || i >= last) {
                            this.currentRunPosition = 1;
                        }
                    }
                }

                if (i >= first && i < last) {
                    this.renderedRuns.push(run)
                }

            }
        },

        nextPage: function() {
            //TODO: look into ways to use JS methods to update/insert new args
            if (run_id) {
                window.location.replace("/marathonprompt/" + prompt_id + "?page=" + String(parseInt(pg) + 1) + "&run_id=" + run_id);
            } else {
                window.location.replace("/marathonprompt/" + prompt_id + "?page=" + String(parseInt(pg) + 1));
            }
        },

        prevPage: function() {
            if (run_id) {
                window.location.replace("/marathonprompt/" + prompt_id + "?page=" + String(parseInt(pg) - 1) + "&run_id=" + run_id);
            } else {
                window.location.replace("/marathonprompt/" + prompt_id + "?page=" + String(parseInt(pg) - 1));
            }
        }
    },

    created: async function() {
        this.prompt = await this.getPrompt();
        this.runs = await this.getRuns();

        console.log(this.runs)

        this.runs.forEach(function(run) {
            run.checkpoints = JSON.parse(run.checkpoints)
            run.path = JSON.parse(run.path)
        })

        this.paginate();

        //console.log(this.runs);

    }
})