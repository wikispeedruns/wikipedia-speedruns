import Vue from 'vue/dist/vue.esm.js';

import { getLocalSprints } from "../modules/localStorage/localStorageSprint.js";


/* This really would be better if we had a SPA huh */

const limit = serverData['limit'];
const offset = serverData['offset'];
const appliedSearch = serverData['search'] || '';

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
        searchInput: appliedSearch,
        appliedSearch: appliedSearch,
    },

    methods : {
        runReplay: function(event) {
            console.log(event)
        },

        escapeHtml: function(text) {
            return String(text)
                .replaceAll('&', '&amp;')
                .replaceAll('<', '&lt;')
                .replaceAll('>', '&gt;')
                .replaceAll('"', '&quot;')
                .replaceAll("'", '&#39;');
        },

        escapeRegex: function(text) {
            return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        },

        highlightMatch: function(text) {
            const safeText = this.escapeHtml(text ?? '-');

            if (!this.appliedSearch) {
                return safeText;
            }

            const pattern = this.escapeRegex(this.appliedSearch);
            const regex = new RegExp(`(${pattern})`, 'ig');
            return safeText.replace(regex, '<mark class="archive-highlight">$1</mark>');
        },

        matchesSearch: function(prompt) {
            if (!this.appliedSearch) {
                return false;
            }

            const searchNeedle = this.appliedSearch.toLowerCase();
            return (prompt.start || '').toLowerCase().includes(searchNeedle)
                || (prompt.end || '').toLowerCase().includes(searchNeedle);
        },

        pageHref: function(nextOffset) {
            const params = new URLSearchParams({
                limit: this.limit,
                offset: Math.max(0, nextOffset),
            });

            if (this.appliedSearch) {
                params.set('search', this.appliedSearch);
            }

            return `?${params.toString()}`;
        },
    },

    created: async function() {
        this.loggedIn = "username" in serverData;

        const params = new URLSearchParams({
            limit,
            offset,
        });

        if (appliedSearch) {
            params.set('search', appliedSearch);
        }

        const response = await fetch(`/api/sprints/archive?${params.toString()}`);
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
