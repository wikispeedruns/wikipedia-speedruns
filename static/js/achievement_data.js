import { achievement_table } from "./modules/achievements.js";
import { achievement_list } from "../achievements/metadata.js";
import { uploadLocalSprints } from "./modules/localStorage/localStorageSprint.js"
import { serverData } from "./modules/serverData.js";

const dataType = document.getElementById('achievement').getAttribute('data');
const RUN_ID = serverData["run_id"];
const LOBBY_ID = serverData["lobby_id"] || null;

var am = new Vue({
    delimiters: ['[[', ']]'],
    el: '#am',
    components: {'achievement-table': achievement_table },

    data: {
        list: achievement_list,
        testData: {},
        empty: true,
        loggedIn: false,
        lobbyId: null
    },

    methods:{

        toggleEmpty: function(){
            this.empty = !this.empty;
        },

        setData: function(data){
            this.testData = data;
        },

        convertData: function(oldData){
            let data = [];
            for(const [name, object] of Object.entries(oldData)){
                let newObject = object;
                newObject["name"] = name;
                data.push(newObject);
            }
            return data;
        },

        getData: async function(){

            if(!this.loggedIn){
                return;
            }

            let data = null;
            if(dataType == 'all'){ // This is getting all achievements for data
                const response = await fetch('/api/achievements/user');
                let tmpData = await response.json();
                data = this.convertData(tmpData);

                // Sort data (array of values) for display
                // Hidden, unachieved at the bottom
                // unachieved (arbitrary order)
                // achieved (sorted by time_achieved)
                data.sort(function(a, b){
                    if(a["achieved"] && b["achieved"]){
                        return b["time_reached"].localeCompare(a["time_reached"]);
                    }
                    else if(a["achieved"]){
                        return -1;
                    }
                    else if(b["achieved"]){
                        return 1;
                    }
                    else{
                        let name1 = a["name"], name2 = b["name"];
                        let hidden1 = achievement_list[name1].hasOwnProperty("hidden"), hidden2 = achievement_list[name2].hasOwnProperty("hidden");
                        if((hidden1 && hidden2) || (!hidden1 && !hidden2)){
                            return 0;
                        }
                        else if(hidden1){
                            return 1;
                        }
                        else if(hidden2){
                            return -1;
                        }
                    }
                });
            }
            else{ // This is getting achievements for the current run
                let localData = JSON.parse(window.localStorage.getItem("lastAchievements"));
                if(localData === null || localData["run_id"] != RUN_ID){
                    const response = await fetch('/api/achievements/get/' + RUN_ID);
                    let tmpData = await response.json();
                    data = this.convertData(tmpData);

                    localData = {
                        "run_id": RUN_ID,
                        "data": data
                    };
                    window.localStorage.setItem("lastAchievements", JSON.stringify(localData));
                }
                else{
                    data = localData["data"];
                }
            }

            if(Object.keys(data).length > 0){
                this.toggleEmpty();
            }
            this.setData(data);
        }
    },

    mounted: async function () {
        this.loggedIn = "username" in serverData;
        this.lobbyId = LOBBY_ID;

        // Make sure that the run gets updated right when play_finish page is updated
        if (this.loggedIn) {
            await uploadLocalSprints();
        }

        await this.getData();
    }
});
