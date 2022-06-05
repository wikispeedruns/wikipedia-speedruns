import { serverData } from "./modules/serverData.js";
import { getLocalSprints } from "./modules/localStorage/localStorageSprint.js";


/* This really would be better if we had a SPA huh */

const limit = serverData['limit'];
const offset = serverData['offset'];
const sort_desc = serverData['sort_desc'];
const sort_prompt = serverData['sort_prompt'];

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
        sort_prompt: sort_prompt,
        loggedIn: false,
    },

    methods : {
        sortButton: function(type='time') {
            let sortBy = this.sort_desc;

            if (type === 'prompt') {
                sortBy = this.sort_prompt; 
            }

            if (sortBy) {
                return `<i class="bi bi-chevron-down"></i>`
            } else {
                return `<i class="bi bi-chevron-up"></i>`
            }
        },

        toggleSort: async function(type) {
            if (type === 'time') {
                this.sort_desc = !this.sort_desc;
                if (this.sort_desc) {
                    this.prompts.sort((a, b) => new Date(a.active_start) - new Date(b.active_start));
                } else {
                    this.prompts.sort((a, b) => new Date(b.active_start) - new Date(a.active_start)); 
                }
            } else if (type === 'prompt') {
                this.sort_prompt = !this.sort_prompt;
                if (this.sort_prompt) {
                    this.prompts.sort((a, b) => a.prompt_id - b.prompt_id);
                } else {
                    this.prompts.sort((a, b) => b.prompt_id - a.prompt_id);
                }
            }
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