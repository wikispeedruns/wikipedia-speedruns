import { fetchJson } from "../fetch.js";
import moment from "moment/moment.js";

var SubmittedSprints = {

    data: function () {
        return {
            pending: [],
            approved: []
        }
	},

    methods: {
        async getPending() {
            try {
                const resp = await (await fetchJson("/api/community_prompts/get_user_pending_sprints")).json();
                this.pending = resp

                this.pending.forEach(
                    el => el['moment_str'] = moment.utc(el.submitted_time).fromNow()
                )
                
            } catch (e) {
                console.log(e);
            }
        },

        async getApproved() {
            try {
                const resp = await (await fetchJson("/api/community_prompts/get_user_approved_sprints")).json();
                this.approved = resp

                this.approved.forEach(function(el) {
                    el['moment_str'] = moment.utc(el.submitted_time).fromNow()
                    if (el.used) {
                        el['publish_moment_str'] = moment.utc(el.active_start).fromNow()
                    } else {
                        el['publish_moment_str'] = "In queue"
                    }
                })
            } catch (e) {
                console.log(e);
            }
        }
	},

    mounted: async function() {
        await this.getPending();
        await this.getApproved();
    },

    template: (`
    <div>
        <div class="row my-3">
            <h5>Approved Sprint Submissions</h5>
            <div class="col table-responsive">
                <template v-if="approved.length > 0">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Submitted</th>
                                <th scope="col">Publish date</th>
                                <th scope="col">Plays</th>
                                <th scope="col">Start</th>
                                <th scope="col">End</th>
                                <th scope="col"><small>Anony.</small></th>
                                <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="prompt in approved" v-cloak>
                                <td><small>{{prompt.moment_str}}</small></td>
                                <td><small>{{prompt.publish_moment_str}}</small></td>
                                <td>{{prompt.total_plays}}</td>
                                <td>{{prompt.start}}</td>
                                <td>{{prompt.end}}</td>
                                <td><small>{{prompt.anonymous ? 'Y' : 'N'}}</small></td>
                                <td><small><a v-if="prompt.used && new Date() > new Date(prompt.active_start)" v-bind:href="'/leaderboard/' + prompt.prompt_id">Leaderboard</a></small></td>
                            </tr>
                        </tbody>
                    </table>
                </template>
                <template v-else>
                    No approved submissions... Yet! 
                    <span v-if="pending.length > 0">
                    Approval time will depend on volume of prompts we receive, so please be patient!
                    </span>
                </template>
            </div>
        </div>
        
        <div class="row my-3">
            <h5>Pending Sprint Submissions</h5>
            <div class="col table-responsive">
                <template v-if="pending.length > 0">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Submitted</th>
                                <th scope="col">Start</th>
                                <th scope="col">End</th>
                                <th scope="col"><small>Anonymous</small></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="prompt in pending" v-cloak>
                                <td><small>{{prompt.moment_str}}</small></td>
                                <td>{{prompt.start}}</td>
                                <td>{{prompt.end}}</td>
                                <td><small>{{prompt.anonymous ? 'Y' : 'N'}}</small></td>
                            </tr>
                        </tbody>
                    </table>
                </template>
                <template v-else>
                    No pending submissions. Try submitting some prompts!
                </template>
            </div>
        </div>
    </div>
    `)
};


var SubmittedMarathons = {

    data: function () {
        return {
            pending: [],
            approved: []
        }
	},

    methods: {
        async getPending() {
            try {
                const resp = await (await fetchJson("/api/community_prompts/get_user_pending_marathons")).json();
                this.pending = resp

                this.pending.forEach(
                    el => el['moment_str'] = moment.utc(el.submitted_time).fromNow()
                )
                
            } catch (e) {
                console.log(e);
            }
        },

        async getApproved() {
            try {
                const resp = await (await fetchJson("/api/community_prompts/get_user_approved_marathons")).json();
                this.approved = resp

                this.approved.forEach(function(el) {
                    el['moment_str'] = moment.utc(el.submitted_time).fromNow()
                })
            } catch (e) {
                console.log(e);
            }
        }
	},

    mounted: async function() {
        await this.getPending();
        await this.getApproved();
    },

    template: (`
    <div>
        <div class="row my-3">
            <h5>Approved Marathon Submissions</h5>
            <div class="col table-responsive">
                <template v-if="approved.length > 0">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Submitted</th>
                                <th scope="col">Plays</th>
                                <th scope="col">Start</th>
                                <th scope="col"><small>Init. Checkpoints</small></th>
                                <th scope="col"><small>Anony.</small></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="prompt in approved" v-cloak>
                                <td><small>{{prompt.moment_str}}</small></td>
                                <td>{{prompt.total_plays}}</td>
                                <td>{{prompt.start}}</td>
                                <td><small>{{prompt.initcheckpoints}}</small></td>
                                <td><small>{{prompt.anonymous ? 'Y' : 'N'}}</small></td>
                            </tr>
                        </tbody>
                    </table>
                </template>
                <template v-else>
                    No approved submissions... Yet! 
                    <span v-if="pending.length > 0">
                    Approval time will depend on volume of prompts we receive, so please be patient!
                    </span>
                </template>
            </div>
        </div>
        
        <div class="row my-3">
            <h5>Pending Marathon Submissions</h5>
            <div class="col table-responsive">
                <template v-if="pending.length > 0">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Submitted</th>
                                <th scope="col">Start</th>
                                <th scope="col"><small>Init. Checkpoints</small></th>
                                <th scope="col"><small>Anonymous</small></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="prompt in pending" v-cloak>
                                <td><small>{{prompt.moment_str}}</small></td>
                                <td>{{prompt.start}}</td>
                                <td><small>{{prompt.initcheckpoints}}</small></td>
                                <td><small>{{prompt.anonymous ? 'Y' : 'N'}}</small></td>
                            </tr>
                        </tbody>
                    </table>
                </template>
                <template v-else>
                    No pending submissions. Try submitting some prompts!
                </template>
            </div>
        </div>
    </div>
    `)
};

export { SubmittedSprints, SubmittedMarathons }
