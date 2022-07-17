import { serverData } from "./modules/serverData.js";
import { profileStatsTable } from "./modules/profileStats.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {'profile-stats-table': profileStatsTable},

    data: {
        profileName: "",
    },

    created: async function() {
        if ("profile_name" in serverData) {
            this.profileName = serverData["profile_name"];
        } 
    },
});
