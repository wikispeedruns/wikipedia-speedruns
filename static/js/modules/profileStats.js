import { serverData } from "./serverData.js";

var profileStatsTable = {

	data: function () {
        return {
            username:"",
            basicStats: {
                username: {
                    field: "Username",
                    val: "--"
                },
                totalratedruns: {
                    field: "Total Attempted Runs",
                    val: "--"
                },
                totalfinishedruns: {
                    field: "Total Completed Runs",
                    val: "--"
                },
                promptsplayed: {
                    field: "Prompts Attempted",
                    val: "--"
                },
                winratio: {
                    field: "Completion Ratio",
                    val: "--"
                },
                profileage: {
                    field: "User Since",
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
        
            try {
            let response = await fetch("/api/profiles/" + this.username + "/stats");
            const runs = await response.json(); 
        
            response = await fetch("/api/profiles/" + this.username);
            const user = await response.json(); 
        
            this.basicStats.username.val = this.username;
            this.basicStats.totalratedruns.val = runs['total_runs'];
            this.basicStats.promptsplayed.val = runs['total_prompts'];
            this.basicStats.totalfinishedruns.val = runs['total_completed_runs'];
            this.basicStats.winratio.val = String(parseInt(runs['total_completed_runs'])*100.0 / parseInt(runs['total_runs'])) + "%"
            let date = new Date(user['join_date']);
            this.basicStats.profileage.val = date.toLocaleDateString();


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
                            <tr v-for="key in Object.keys(basicStats)" v-bind:key="">
                                <td>{{basicStats[key].field}}: </td>
                                <td>{{basicStats[key].val}}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `)
};

export {profileStatsTable}
