import { profileStatsTable } from "./modules/profileStats.js";

var app = new Vue({
    el: '#app',
    components: {'profile-stats': profileStatsTable }
});
