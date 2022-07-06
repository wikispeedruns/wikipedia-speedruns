import { profileStatsTable } from "./modules/profileStats.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {'profile-stats': profileStatsTable},
});
