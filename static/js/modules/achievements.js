
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
            imgpath: this.basepath,
            achieved: this.achievementdata['achieved'],
            multirun: this.achievementdata['out_of'] ? true : false,
            progress: ''
        }
    },

    created: function () {
        if (!this.achieved) {
            this.imgpath += 'locked200px.png'
        } else if (this.img) {
            this.imgpath += this.img
        } else {
            this.imgpath += 'achieved200px.png'
        }

        if (this.achieved) {
            this.progress = "Achieved " + moment.utc(this.achievementdata['time_reached']).fromNow()
        } else if (this.multirun) {
            this.progress = String((this.achievementdata['reached'] / this.achievementdata['out_of'] * 100.0).toFixed(1))+"%"
        }
    },

    template: (`
        <tr>
            <td class="col-auto"><img v-bind:src="imgpath" height='75' width='75'></td>
            <td v-if="!achieved && hidden">
                <b class="text-muted">Hidden achievement...</b>
            </td>
            <td v-else>
                <b>{{display_name}}</b><br>{{description}}
            </td>
            <td v-if="achieved || (multirun && !hidden)"><small class="text-muted">{{progress}}</small></td>
            <td v-else></td>
        </tr>
    `)
}


var achievement_table = {

    props: [
        "list",
        "achievements", //array of achieved names,
        "basepath"
    ],

    components: {
        'achievement': achievement
    },

    created: function () {

        //console.log(this.list)
    },

	template: (`
        <div class="col-sm-10">
            <div class="card">
                <div class="card-body">
                <table class="table table-hover">
                    <tbody>
                    <achievement v-for="(entry, name) in achievements" v-bind:key="name"
                        v-bind:display_name="list[name]['display_name']"
                        v-bind:description="list[name]['description']"
                        v-bind:hidden="list[name]['hidden']"
                        v-bind:img="list[name]['img']"
                        v-bind:basepath="basepath"
                        v-bind:achievementdata="achievements[name]"
                    ></achievement>
                    </tbody>
                </table>
                </div>
            </div>
        </div>
    `)
};

export {achievement_table}
