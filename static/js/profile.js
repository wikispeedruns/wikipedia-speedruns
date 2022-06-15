import { profileStatsTable } from "./modules/profileStats.js";
import { achievement_table } from "./modules/achievements.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {'profile-stats': profileStatsTable, 'achievement-table': achievement_table },

    data: {

        list: achievement_list,

        testData: {
            "bathroom": {
                "time_reached": "2009-06-15T13:45:30",
                "achieved": 1
            }, 
            "usa": {
                "time_reached": "2019-06-15T13:45:30",
                "achieved": 0,
                "reached": 7,
                "out_of": 50
            }, 
            "sparta": {
                "time_reached": "2009-06-15T13:45:30",
                "achieved": 0
            }, 
            "fastest_gun_alive": {
                "time_reached": "2019-06-15T13:45:30",
                "achieved": 1
            }, 
            "meta": {
                "time_reached": "2019-06-15T13:45:30",
                "achieved": 1
            }}
    }
});
