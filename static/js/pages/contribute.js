import Vue from 'vue/dist/vue.esm.js';

import { MarathonBuilder } from '../modules/prompts/marathon-submit.js';
import { SprintBuilder } from '../modules/prompts/sprint-submit.js';
import { SubmittedSprints, SubmittedMarathons } from '../modules/prompts/submitted-prompts.js';

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'marathon-builder': MarathonBuilder,
        'sprint-builder': SprintBuilder,
        'submitted-sprints': SubmittedSprints,
        'submitted-marathons': SubmittedMarathons
    },
    data: {
        tab: "",
        loggedIn: false
    },

    created: async function() {
        this.loggedIn = "username" in serverData
    },
}); // End vue