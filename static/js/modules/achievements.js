
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
            multirun: this.achievementdata['out_of'] ? true : false,
            progress: ''
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
                <b>{{display_text}}</b><br>{{description}}
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
        "basepath",
        "profile",
        "total",
        "achieved"
    ],

    components: {
        'achievement': achievement
    },

    created: function () {

        //console.log(this.list)
    },

    //Achievements - {{achieved}}/{{total}}

    template: (`
    <div class="col-sm-10">
        <div class="card">
            <div class="card-body">
            <table class="table table-hover">
                <thead v-if="profile">
                    <td colspan=4><h3>Achievements - {{achieved}}/{{total}} Unlocked</h3></td>
                </thead>
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
            </table>
            </div>
        </div>
    </div>
    `)
};

export {achievement_table}
