import moment from "moment/moment.js";

import { achievement_list } from "../../achievements/metadata.js";
import { getLocalStorage, setLocalStorage } from "./localStorage/localStorage.js";

var achievement = {
    props: [
        'display_name',
        'description',
        'hidden',
        'img',
        'basepath',
        'achievementdata',
    ],

    data: function () {
        return {
            display_text: '',
            imgpath: this.basepath,
            achieved: this.achievementdata['achieved'],
            multirun: this.achievementdata['out_of'] != 1,
            progress: '',
            progressPercent: 0,
            color: '#ccffee'
        }
    },

    computed: {
        createBackground() {
            return `linear-gradient(90deg, ${this.color} ${this.progressPercent}%, transparent ${this.progressPercent}%)`;
        }
    },

    created: function () {
        this.display_text = this.$props.display_name;
        if (this.hidden){
            this.display_text += ' - (Hidden)';
        }

        if (!this.achieved) {
            this.imgpath += 'locked200px.png'
        } else if (this.img) {
            this.imgpath += this.img
        } else {
            this.imgpath += 'achieved200px.png'
        }

        this.progressPercent = parseInt(this.achievementdata['reached'] / this.achievementdata['out_of'] * 100.0);

        if (this.achieved) {
            this.progress = "Achieved " + moment.utc(this.achievementdata['time_reached']).fromNow()
        } else {
            this.progress = String(this.progressPercent)+"%";
        }
    },

    template: (`
        <tr :style="{ 'background': achieved ? 'none' : createBackground }">
            <td class="col-auto"><img v-bind:src="imgpath" height='75' width='75'></td>
            <td v-if="!achieved && hidden">
                <b class="text-muted">Hidden achievement...</b>
            </td>
            <td v-else>
                <b>{{display_text}}</b><br>{{description}}
            </td>
            <td><small class="text-muted" style="display:block; text-align:center;">{{progress}}</small></td>
        </tr>
    `)
}


var achievement_table = {

    props: [
        "list",
        "achievements", //array of achieved names,
        "basepath",
        "profile",
        "total",
        "achieved",
    ],

    components: {
        'achievement': achievement
    },

    created: function () {

        //console.log(this.list)
    },

    template: (`
    <tbody>
        <achievement v-for="item in achievements" v-bind:key="item.name"
            v-bind:display_name="list[item.name]['display_name']"
            v-bind:description="list[item.name]['description']"
            v-bind:hidden="list[item.name]['hidden']"
            v-bind:img="list[item.name]['img']"
            v-bind:basepath="basepath"
            v-bind:achievementdata="item"
        ></achievement>
    </tbody>
    `)
};



// Sort data (array of values) for display
// Hidden, unachieved at the bottom
// unachieved (arbitrary order)
// achieved (sorted by time_achieved)
function default_cmp(a, b){
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

        let name1 = a["name"], name2 = b["name"], progress1 = a["reached"]/a["out_of"], progress2 = b["reached"]/b["out_of"]
        let hidden1 = achievement_list[name1].hasOwnProperty("hidden"), hidden2 = achievement_list[name2].hasOwnProperty("hidden");
        if((hidden1 && hidden2) || (!hidden1 && !hidden2)){
            return progress2 - progress1;
        }
        else if(hidden1){
            return 1;
        }
        else if(hidden2){
            return -1;
        }
    }
}

const achievement_storage = "lastAchievements";

var achievements = {
    components: {'achievement-table': achievement_table },

    props: {

        loggedIn: Boolean,

        // username for profile page
        username: {
            type: String,
            default: null
        },

        // sprint run specific
        runId: {
            type: Number,
            default: -1
        },
        isSprint: {
            type: Boolean,
            default: null
        },

        basepath: String
    },

    data: function () {
        return {
            list: achievement_list,
            data: {},

            isProfile: null,

            // profile page
            total: 0,
            achieved: 0,
        }
    },

    computed: {
        isEmpty() {
            return this.count == 0;
        },
        count() {
            return Object.keys(this.data).length;
        },
        title() {
            if(this.isProfile) return `Achievements - ${this.achieved}/${this.total} Unlocked`;
            else {
                if(!this.isSprint) return `Unlock achievements in public prompts...`;
                if(!this.loggedIn) return `Login to check possible New Achievements!`;
                else return this.isEmpty ? `No new achievements unlocked` :
                            this.count == 1 ? `${this.achieved} New Achievement!` :
                                              `${this.achieved} New Achievements!`;
            }
        }
    },

    methods:{

        convertData: function(oldData){
            let data = [];
            let total = 0, achieved = 0;
            for(const [name, object] of Object.entries(oldData)){
                let newObject = object;
                newObject["name"] = name;
                data.push(newObject);

                if(newObject["achieved"]) achieved ++;
                total ++;
            }

            data.sort(default_cmp);
            this.total = total;
            this.achieved = achieved;
            return data;
        },

        getData: async function(){

            let data = null;

            if(this.isProfile){ // This is getting all achievements for data
                const response = await fetch('/api/achievements/user/' + this.username);
                if(response.status != 200){
                    console.log("error fetching achievements for user");
                    return;
                }

                let tmpData = await response.json();
                data = this.convertData(tmpData);
            }
            else{ // This is getting achievements for the current run

                if(!this.loggedIn || !this.isSprint){
                    return;
                }

                let localData = getLocalStorage(achievement_storage);
                if(localData === null || localData["run_id"] != this.runId){
                    const response = await fetch('/api/achievements/process/' + this.runId, {method: 'PATCH'});
                    if(response.status != 200) {
                        console.log("run is either never finished or already considered for achievements");
                        return;
                    }

                    let tmpData = await response.json();
                    data = this.convertData(tmpData);
                    localData = {
                        "run_id": this.runId,
                        "data": data
                    };
                    setLocalStorage(localData);
                }
                else{
                    data = localData["data"];
                }
            }
            this.data = data;
        }
    },

    mounted: async function () {
        this.isProfile = (this.runId == -1);

        await this.getData();
    },

    template: (`
    <div class="col-sm-10" style="padding-top:15px;">
        <div class="card">
            <div class="card-body">
            <table class="table table-hover">
                <thead>
                    <td colspan=4><h3>{{title}}</h3></td>
                </thead>
                <achievement-table class="py-4"
                    v-bind:list="list"
                    v-bind:achievements="data"
                    v-bind:basepath="basepath"
                    v-bind:profile="isProfile"
                    v-bind:total="total"
                    v-bind:achieved="achieved"
                ></achievement-table>
            </table>
            </div>
        </div>
    </div>
    `)
};


export { achievements, achievement_table}
