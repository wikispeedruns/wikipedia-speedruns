import Vue from 'vue/dist/vue.esm.js';

import { ArticleRenderer } from "../modules/game/articleRenderer.js";

const run_id = serverData["run_id"];
const div_name = "wikipedia-frame";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',

    data: {
        firstArticle: "",
        lastArticle: "",
        currentPathIndex: 0,
        path: [],
        renderer: null,
    },

    methods: {
        previous: async function () {
            console.log(this.currentPathIndex);
            document.getElementById(div_name).innerHTML = "";
            await this.renderer.loadPage(this.path[--this.currentPathIndex]);
        },
        next: async function() {
            console.log(this.currentPathIndex);
            document.getElementById(div_name).innerHTML = "";
            await this.renderer.loadPage(this.path[++this.currentPathIndex]);
        },
    },

    mounted: async function() {
        if (run_id == "") {
            alert("No run id found");
            return;
        }
        const response = await fetch("/api/runs/" + run_id);
        if (response.status != 200) {
            const error = await response.text();
            alert(error);
            return;
        }
        const run = await response.json();
        console.log(run);
        this.path = run['path'].map((entry) => entry["article"]);
        this.firstArticle  = this.path[0];
        this.lastArticle = this.path[this.path.length - 1];

        this.renderer = new ArticleRenderer(document.getElementById(div_name), (_) => {});
        await this.renderer.loadPage(this.path[0]);
    },

});
