import { serverData } from "./modules/serverData.js";
import { getLocalSprints } from "./modules/localStorage/localStorageSprint.js";


/* This really would be better if we had a SPA huh */

const limit = serverData['limit'];
const offset = serverData['offset'];
const sort_desc = serverData['sort_desc'];

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        prompts: [],
        page: 0,
        numPages: 0,

        limit: limit,
        offset: offset,
        sort_desc: sort_desc,
        loggedIn: false,
    },

    methods : {
        sortButton: function() {
            if (this.sort_desc) {
                return `<i class="bi bi-chevron-down"></i>`
            } else {
                return `<i class="bi bi-chevron-up"></i>`
            }
        },

        toggleSort: async function() {
            const dest = `?limit=${limit}&offset=0&sort_desc=${!this.sort_desc}`;
            const response = await fetch("/api/sprints/archive" + dest);
            const resp = await response.json();
            this.prompts = resp['prompts'];
            this.page = 1;
            this.offset = 0;
            this.sort_desc = !this.sort_desc;
        },

        runReplay: function(event) {
            console.log(event)
        }
    },

    created: async function() {
        this.loggedIn = "username" in serverData;

        const response = await fetch(`/api/sprints/archive?limit=${limit}&offset=${offset}&sort_desc=${sort_desc}`);
        const resp = await response.json();

        this.prompts = resp['prompts'];

        this.numPages = Math.ceil(resp['numPrompts'] / limit);
        this.page = Math.floor(1 + offset / limit);

        this.limit = limit;
        this.offset = offset;
        this.sort_desc = sort_desc;

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
