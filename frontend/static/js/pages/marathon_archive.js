import Vue from 'vue/dist/vue.esm.js';

import { getLocalMarathons } from "../modules/localStorage/localStorageMarathon.js";


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
        username: null,
        savedGames: [],
    },

    methods : {
        runReplay: function(event) {
            console.log(event)
        }
    },

    created: async function() {
        this.loggedIn = "username" in serverData;
        if (this.loggedIn) {this.username = serverData['username']}
        
        const response = await fetch(`/api/marathon/archive?limit=${limit}&offset=${offset}`);
        const resp = await response.json();

        this.prompts = resp['prompts'];

        this.numPages = Math.ceil(resp['numPrompts'] / limit);
        this.page = Math.floor(1 + offset / limit);

        this.limit = limit;
        this.offset = offset;

        if (!this.loggedIn) {

            const localMarathons = getLocalMarathons();

            for (let prompt of this.prompts){
                for (let run_id of Object.keys(localMarathons)) {
                    if (parseInt(localMarathons[run_id].prompt_id) === prompt.prompt_id) {
                        prompt.played = true
                    }
                }
            }
        }

        let keys = Object.keys(localStorage),
        i = keys.length;

        while ( i-- ) {
            if ( keys[i].substring(0, 5) == 'WS-M-') {
                this.savedGames.push( JSON.parse(localStorage.getItem(keys[i])) );
            }
        }
        for (let prompt of this.prompts) {
            prompt.savedGamePresent = false
            for (let savedGame of this.savedGames) {
                if (parseInt(savedGame.prompt_id) === prompt.prompt_id) {
                    prompt.savedGamePresent = true
                }
            }
        }

    }
})