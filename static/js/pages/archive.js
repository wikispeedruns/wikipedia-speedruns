import Vue from 'vue/dist/vue.esm.js';

import { getLocalSprints } from "../modules/localStorage/localStorageSprint.js";


/* This really would be better if we had a SPA huh */

const limit = serverData['limit'];
const offset = serverData['offset'];

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        prompts: [],
        page: 0,
        numPages: 0,

        limit: limit,
        offset: offset,
        loggedIn: false,
    },

    methods : {
        runReplay: function(event) {
            console.log(event)
        }
    },

    created: async function() {
        this.loggedIn = "username" in serverData;

        const response = await fetch(`/api/sprints/archive?limit=${limit}&offset=${offset}`);
        const resp = await response.json();

        this.prompts = resp['prompts'];

        this.numPages = Math.ceil(resp['numPrompts'] / limit);
        this.page = Math.floor(1 + offset / limit);

        this.limit = limit;
        this.offset = offset;

        if (!this.loggedIn) {

            const localSprints = getLocalSprints();

            for (let prompt of this.prompts){
                for (let run_id of Object.keys(localSprints)) {
                    if (parseInt(localSprints[run_id].prompt_id) === prompt.prompt_id) {
                        prompt.played = true
                    }
                }
            }
        }

    }
})