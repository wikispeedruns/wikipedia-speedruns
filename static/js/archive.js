import { serverData } from "./modules/serverData.js";

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

        limit: 0,
        offset: 0,
        loggedIn: false,
    },

    created: async function() {
        if ("username" in serverData) {
            this.loggedIn = true;
        }
        
        const response = await fetch(`/api/sprints/archive?limit=${limit}&offset=${offset}`);
        const resp = await response.json();

        this.prompts = resp['prompts'];

        this.numPages = Math.ceil(resp['numPrompts'] / limit);
        this.page = Math.floor(1 + offset / limit);

        this.limit = limit;
        this.offset = offset;
    }
})
