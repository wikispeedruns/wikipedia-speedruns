import Vue from 'vue/dist/vue.esm.js';

import { profileStatsTable } from "../modules/profileStats.js";
import { achievements } from "../modules/achievements.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'profile-stats-table': profileStatsTable,
        'achievements': achievements
    },

    data: {
        profileName: "",
    },

    created: async function() {
        if ("profile_name" in serverData) {
            this.profileName = serverData["profile_name"];
        }
    },
});
