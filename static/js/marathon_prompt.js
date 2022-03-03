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

        getPromptID: function() {
            return prompt_id;
        },

        getRunID: function() {
            return this.run_id;
        },
    },

    mounted: async function() {
        this.prompt = await this.getPrompt();
        this.runs = await this.getRuns();

    }
})