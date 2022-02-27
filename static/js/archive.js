import { serverData } from "./modules/serverData.js";

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

        limit: 0,
        offset: 0,
        sort_desc: 0
    },

    created: async function() {
        const response = await fetch(`/api/sprints/archive?limit=${limit}&offset=${offset}&sort_desc=${sort_desc}`);
        const resp = await response.json();

        this.prompts = resp['prompts'];

        this.numPages = Math.ceil(resp['numPrompts'] / limit);
        this.page = Math.floor(1 + offset / limit);

        this.limit = limit;
        this.offset = offset;
        this.sort_desc = sort_desc;
    }
})
