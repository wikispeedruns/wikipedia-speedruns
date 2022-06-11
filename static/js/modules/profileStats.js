import { serverData } from "./serverData.js";

var profileStatsTable = {

	data: function () {
        return {
            username:"",
            basic_stats: {
                username: {
                    field: "Username",
                    val: "--"
                },
                totalratedruns: {
                    field: "Total Runs",
                    val: "--"
                },
                profileage: {
                    field: "Member Since",
                    val: "--"
                },
            }
        }
	},

    created: async function () {
        this.username = serverData["username"];
        await this.get_data();
    },

	methods: {

        async get_data() {
            let response = await fetch("/api/profiles/" + this.username + "/stats");
            const runs = await response.json(); 
        
            response = await fetch("/api/profiles/" + this.username);
            const user = await response.json(); 
        
            this.update_data(runs, user);
        },

        update_data(runs, user) {
            try {
                this.basic_stats.username.val = this.username;
                this.basic_stats.totalratedruns.val = runs['total_prompts'];
                let date = new Date(user['join_date']);
                this.basic_stats.profileage.val = date.toLocaleDateString();
            } catch (error) {
                console.error(error);
                //window.location.href = "/error";
            }
        },
	},

	template: (`
        <div class="col-sm-10">
            <div class="card">
                <div class="card-body">
                <table class="table table-striped table-hover">
                    <thead class="thead-light">
                        <td colspan=2><h4>Basic Profile Stats</h4></td>
                    </thead>
                    <tbody>
                    <tr v-for="key in Object.keys(basic_stats)" v-bind:key="">
                        <td>{{basic_stats[key].field}}: </td>
                        <td>{{basic_stats[key].val}}</td>
                    </tr>
                    </tbody>
                </table>
                </div>
            </div>
        </div>
    `)
};

export {profileStatsTable}
