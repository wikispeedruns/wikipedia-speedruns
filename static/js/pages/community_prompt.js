import Vue from 'vue/dist/vue.esm.js';

import { fetchAsync, fetchJson } from "../modules/fetch.js";
import { getArticleTitle, articleCheck } from "../modules/wikipediaAPI/util.js";

import { MarathonBuilder } from '../modules/prompts/marathon-submit.js';

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'marathon-builder': MarathonBuilder
    },
    data: {
        startPrompt: "",
        endPrompt: "",
        anonymous: true
    },

    methods: {
        async newPrompt(event) {

            const start = await getArticleTitle(this.startPrompt);
            if (!start) {
                alert(`Invalid article name "${this.startPrompt}"`);
                return;
            }

            const end = await getArticleTitle(this.endPrompt);
            if (!end) {
                alert(`Invalid article name "${this.endPrompt}"`);
                return;
            }

            const checkRes = await articleCheck(this.endPrompt);
            if ('warning' in checkRes) {
                alert(checkRes["warning"]);
                return;
            }

            try {
                const response = await fetchJson("/api/community_prompts/submit_sprint_prompt", "POST", {
                    "start": start,
                    "end": end,
                    "anonymous": this.anonymous
                })

            } catch (e) {
                console.log(e);
            }
        }

    } // End methods
}); // End vue