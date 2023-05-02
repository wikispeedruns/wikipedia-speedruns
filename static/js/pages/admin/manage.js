import Vue from 'vue/dist/vue.esm.js';

import { fetchAsync, fetchJson } from "../../modules/fetch.js";
import { getArticleTitle, articleCheck } from "../../modules/wikipediaAPI/util.js";

import { MarathonBuilder } from '../../modules/prompts/marathon-submit.js';
import { SprintBuilder } from '../../modules/prompts/sprint-submit.js';

Vue.component('prompt-item', {
    props: ['prompt', 'unused'],

    data: function() {
        return {
            ratedChecked: this.prompt.rated
        }
    },

    methods: {

        async deletePrompt() {
            const resp = await fetchJson("/api/sprints/" + this.prompt.prompt_id, "DELETE");

            if (resp.status == 200) this.$emit('delete-prompt')
            else alert(await resp.text())
        },

        async removePrompt() {
            const resp = await fetchJson("/api/sprints/set_unused/" + this.prompt.prompt_id, "PATCH");

            if (resp.status == 200) this.$emit('remove-prompt')
            else alert(await resp.text())
        },
    },

    template: (`
    <li>
        <strong>{{prompt.prompt_id}}</strong>: {{prompt.start}} -> {{prompt.end}}

        <span v-if="prompt.used && !prompt.rated">
            {{prompt.active_start}} - {{prompt.active_end}}
        </span>

        <button v-on:click="deletePrompt" type="button" class="btn btn-default">
            <i class="bi bi-trash"></i>
        </button>
        <button v-if="!unused" v-on:click="removePrompt" type="button" class="btn btn-default">
            <i class="bi bi-arrow-counterclockwise"></i>
        </button>
    </li>`)
});

// TODO maybe these should load the date stuff themselves (At least on update)
Vue.component('prompt-set', {
    props: ['start', 'end', 'rated', 'prompts'],

    methods: {
        async moveToDay() {
            const response = await fetchJson("/api/sprints/" + this.promptToAdd, "PATCH", {
                "startDate": this.start,
                "endDate": this.end,
                "rated": this.rated,
            });

            if (response.status != 200) {
                alert(await response.text());
            } else {
                this.$emit('move-prompt') // TODO reload just this box instead of triggering a full realead
            }
        },
    },

    data: function() {
        return {
            promptToAdd: 0
        }
    },

    template: (`
    <div>
        <p v-if="start === end">{{start.substring(5)}}</p>

        <ul class="ps-3 my-0">
            <prompt-item
                v-for="p in prompts"
                v-bind:prompt="p"
                v-bind:key="p.prompt_id"
                v-on="$listeners"
            >
            </prompt-item>
        </ul>

        <form class="form-inline" v-on:submit.prevent="moveToDay">
            <div class="input-group input-group-sm mb-2">
                <input class="form-control" v-model="promptToAdd">
                <div class="input-group-append">
                    <button type="submit" class="btn btn-dark">
                        <i class="bi bi-arrow-right-square"></i>
                    </button>
                </div>
            </div>
        </form>


    </div>
    `)
});

Vue.component('path-checker', {
    data: function() {
        return {
            pathStart: "",
            pathEnd: "",

            path: [],
        }
    },

    methods: {
        async pathCheck() {

            const res = await fetchAsync("/api/scraper/path", "POST", {
                "start": this.pathStart,
                "end": this.pathEnd
            });
            this.path = res["Articles"];
        }
    },

    template: (`
    <div>
        <p> Check for shortest paths of any 2 articles here: </p>
        <form id="checkPath"  v-on:submit.prevent="pathCheck">
            <label for="pathStart">Start Article:</label>
            <input type="text" name="pathStart" v-model="pathStart">
            <label for="pathEnd">End Article:</label>
            <input type="text" name="pathEnd" v-model="pathEnd">
            <button type="submit">Check for shortest path</button>
        </form>

        <p> {{path}} </p>
    </div>
    `)
});

Vue.component('path-generator', {
    data: function() {
        return {
            prompts: []
        }
    },


    methods: {
        async genPrompt() {
            try {
                const resp = await fetchAsync("/api/scraper/gen_prompts", 'POST');

                let prompt = {};

                prompt.start = resp['Prompts'][0][0];
                prompt.end = resp['Prompts'][0][1];

                const res = await fetchAsync("/api/scraper/path", "POST", {
                    "start": prompt.start,
                    "end": prompt.end
                });
                prompt.path = res["Articles"];

                this.prompts.push(prompt);
            } catch (e) {
                console.log(e);
            }
        }
    },

    template: (`
        <div>
            <button id="genPromptButton" v-on:click="genPrompt">Click to generate a random prompt</button>
            <ul>
                <li v-for="p in prompts">
                    {{p.start}} -> {{p.end}}: ({{p.path}})
                </li>
            </ul>
        </div>
    `)

});

Vue.component('approve-pending', {
    data: function() {
        return {
            prompts: []
        }
    },

    methods: {
        async getPending() {
            try {
                const resp = await (await fetchJson("/api/community_prompts/get_pending_sprints")).json();
                this.prompts = resp
            } catch (e) {
                console.log(e);
            }
        },

        async approve(prompt_id, anonymous) {
            try {
                await fetchJson("/api/community_prompts/approve_sprint", "POST", {
                    pending_id: prompt_id,
                    anonymous: anonymous
                });
            } catch (e) {
                console.log(e);
            }
            await this.getPending();
        },

        async reject(prompt_id) {
            try {
                await fetchJson("/api/community_prompts/reject_sprint", "DELETE", {
                    pending_id: prompt_id
                });
            } catch (e) {
                console.log(e);
            }
            await this.getPending();
        }
    },

    created: async function() {
        await this.getPending();
    },

    template: (`
    <div class="card-body">
        <template v-if="prompts.length > 0">
            Cmty pending Sprints
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th scope="col">Pending ID</th>    
                        <th scope="col">Username</th>
                        <th scope="col">Date Submitted</th>
                        <th scope="col">Start</th>
                        <th scope="col">End</th>
                        <th scope="col">Anonymous</th>
                        <th scope="col"></th>
                        <th scope="col"></th>
                        <th scope="col"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="prompt in prompts" v-cloak>
                        <td>{{prompt.pending_prompt_id}}</td>
                        <td>{{prompt.username}}</td>
                        <td>{{prompt.submitted_time}}</td>
                        <td>{{prompt.start}}</td>
                        <td>{{prompt.end}}</td>
                        <td>{{prompt.anonymous}}</td>
                        <td><button v-on:click="approve(prompt.pending_prompt_id, prompt.anonymous)">Approve</button></td>
                        <td><button v-on:click="approve(prompt.pending_prompt_id, 1)">Approve as anon.</button></td>
                        <td><button v-on:click="reject(prompt.pending_prompt_id)">Reject</button></td>
                    </tr>
                </tbody>
            </table>
        </template>
        <template v-else>
            No pending prompts
        </template>
    </div>
    `)
});


Vue.component('marathon-item', {
    props: ['prompt'],

    methods: {

        async deletePrompt() {
            const resp = await fetchJson("/api/marathon/delete/" + this.prompt.prompt_id, "DELETE");

            if (resp.status == 200) this.$emit('delete-prompt')
            else alert(await resp.text())

            app.getPrompts();
        },

        async copyPrompt() {
            this.$emit('copy-prompt');
        }
    },

    template: (`
    <li>
        <strong>{{prompt.prompt_id}}</strong>: {{prompt.start}}
        <div>{{prompt.initcheckpoints}}</div>
        <div>{{prompt.checkpoints}}</div>
        <button v-on:click="deletePrompt" type="button" class="btn btn-default" >
            <i class="bi bi-trash"></i>
        </button>
    </li>`)
});


Vue.component('marathon-pending-item', {
    props: ['prompt'],

    methods: {

        async approve(prompt_id, anonymous) {
            try {
                await fetchJson("/api/community_prompts/approve_marathon", "POST", {
                    pending_id: prompt_id,
                    anonymous: anonymous
                });
            } catch (e) {
                console.log(e);
            }
            await this.$emit('refresh');
        },

        async reject(prompt_id) {
            try {
                await fetchJson("/api/community_prompts/reject_marathon", "DELETE", {
                    pending_id: prompt_id
                });
            } catch (e) {
                console.log(e);
            }
            await this.$emit('refresh');
        }
    },

    template: (`
    <li>
        <strong>{{prompt.pending_prompt_id}}</strong>: {{prompt.username}}, {{prompt.submitted_time}}, {{prompt.anonymous}}
        <div>{{prompt.start}}</div>
        <div>{{prompt.initcheckpoints}}</div>
        <div>{{prompt.checkpoints}}</div>
        <div>
            <button v-on:click="approve(prompt.pending_prompt_id, prompt.anonymous)">Approve</button></td>
            <button v-on:click="approve(prompt.pending_prompt_id, 1)">Approve as anon.</button></td>
            <button v-on:click="reject(prompt.pending_prompt_id)">Reject</button>
        </div>
    </li>`)
});



Vue.component('marathon-list', {

    data: function() {
        return {
            prompts: []
        }
    },

    created: async function(){
        await this.getMarathonPrompts();
    },

    methods: {

        async getMarathonPrompts() {
            const marathonprompts = await (await fetchJson("/api/marathon/all")).json();
            this.prompts = marathonprompts;
        },

        copyPrompt: function(prompt) {
            this.start = prompt['start']
            this.startcp = JSON.parse(prompt['initcheckpoints'])
            this.cp = JSON.parse(prompt['checkpoints'])
            this.seed = prompt['seed']
            this.$forceUpdate();
        }
    },

    template: (`
        <div>
            <div class="row">
                <div class="col px-0"> <div class="card"> <div class="card-body">
                    <h4> Marathon prompts: </h4>
                    <ul>
                        <marathon-item
                            v-for="p in prompts"
                            v-bind:prompt="p"
                            v-bind:key="p.prompt_id"
                        >
                        </marathon-item>
                    </ul>
                </div></div></div>
            </div>
        </div>
    `)
});

Vue.component('marathon-pending-list', {

    data: function() {
        return {
            prompts: []
        }
    },

    created: async function(){
        await this.getMarathonPendingPrompts();
    },

    methods: {

        async getMarathonPendingPrompts() {
            const marathonprompts = await (await fetchJson("/api/community_prompts/get_pending_marathons")).json();
            this.prompts = marathonprompts;
        },
    },

    template: (`
        <div>
            <div class="row">
                <div class="col px-0"> <div class="card"> <div class="card-body">
                    <h4> Pending marathon prompts: </h4>
                    <ul>
                        <marathon-pending-item
                            v-for="p in prompts"
                            v-bind:prompt="p"
                            v-bind:key="p.prompt_id"
                            v-on:refresh="getMarathonPendingPrompts"
                        >
                        </marathon-pending-item>
                    </ul>
                </div></div></div>
            </div>
        </div>
    `)
});




var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'marathon-builder': MarathonBuilder,
        'sprint-builder': SprintBuilder
    },
    data: {
        unused: [],
        weeks: [],

        startPrompt: "",
        endPrompt: "",

        tab: "sprint-build"
    },

    created: async function() {
        await this.getPrompts();
    },

    methods: {
        toISODate(date) {
            return date.toISOString().substring(0, 10);
        },
        async getPrompts() {
            const prompts = await (await fetchJson("/api/sprints/managed")).json();
            this.unused = prompts.filter(p => !p["used"]);
            const used = prompts.filter(p => p["used"]);

            let daily = used.filter(p => p["rated"]);
            let weeklys = used.filter(p => !p["rated"]);

            let nextDailys = {};
            let nextWeeklys = {};

            daily.forEach((p) => {
                // Get iso date (yyyy-mm-dd)
                const key = p["active_start"].substring(0, 10);
                if (!nextDailys[key]) {
                    nextDailys[key] = [];
                }
                nextDailys[key].push(p);
            });

            weeklys.forEach((p) => {
                const key = p["active_start"].substring(0, 10);
                if (!nextWeeklys[key]) {
                    nextWeeklys[key] = [];
                }
                nextWeeklys[key].push(p);
            })

            let cur = new Date();

            // Change cur to first day of this week
            cur.setUTCDate(cur.getUTCDate() - cur.getUTCDay());

            this.weeks = [];
            for (let i = 0; i < 2; i++) {
                let end = new Date(cur)
                end.setDate(cur.getDate() + 7);
                this.weeks.push({
                    start: this.toISODate(cur),
                    end: this.toISODate(end),
                    days: [],
                    prompts: nextWeeklys[this.toISODate(cur)]
                });


                for (let j = 0; j < 7; j++) {

                    const day = new Date(cur);
                    this.weeks[i].days.push({
                        "date": this.toISODate(day),
                        "prompts": nextDailys[this.toISODate(day)] || []
                    });

                    cur.setDate(cur.getDate() + 1);
                }
            }
        },

    } // End methods
}); // End vue