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
        tab: ""
    },

    created: async function() {
        if (!("username" in serverData)) {
            alert("Must be logged in to view this page!")
            window.location.href = "/login";  // redirect home if not logged in
        }
    },
}); // End vue