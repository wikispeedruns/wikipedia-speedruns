import Vue from 'vue/dist/vue.esm.js';

import { fetchAsync, fetchJson } from "../../modules/fetch.js";
import { getArticleTitle, articleCheck } from "../../modules/wikipediaAPI/util.js";

Vue.component('prompt-item', {
    props: ['prompt'],

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
        <button v-on:click="copyPrompt" type="button" class="btn btn-default" >
            <i class="bi bi-clipboard"></i>
        </button>
    </li>`)
});




Vue.component('marathon-section', {

    props: ['marathonprompts'],

    data: function() {
        return {
            start: "United States",
            startcp: [],
            cp: [],
            seed: "0",
        }
    },

    methods: {
        submitPrompt: async function() {
            try {

                if (this.startcp.length != 5) throw new Error("Need 5 starting checkpoints");
                if (this.cp.length < 40) throw new Error("Need 40+ checkpoints");

                const response = await fetchJson("/api/marathon/add/", 'POST', {'data': this.$data })

                if (response.status != 200) {
                    // For user facing interface, do something other than this
                    alert(await response.text());
                    return;
                }

                document.getElementById("generatedMarathonText").innerHTML = "Prompt submit success. Refresh to see recently added prompt"

            } catch (e) {
                document.getElementById("generatedMarathonText").innerHTML = e
                console.log(e);
            }
        },

        addArticle: async function(mode) {
            if (document.getElementById("inputField").value.length < 1) return;

            let a = await getArticleTitle(document.getElementById("inputField").value)

            if (this.cp.includes(a) || this.startcp.includes(a)) {
                document.getElementById("generatedMarathonText").innerHTML = "Article already exists"
                return
            }

            if (mode == 0) {
                this.start = a
            } else if (mode == 1) {
                this.startcp.push(a)
            } else if (mode == 2) {
                this.startcp.unshift(a)
            } else if (mode == 3) {
                this.cp.push(a)
            } else if (mode == 4) {
                this.cp.unshift(a)
            }
        },

        moveup: function (ind, mode) {
            if (ind == 0) return;
            if (mode == 0) {
                [this.startcp[ind-1], this.startcp[ind]] = [this.startcp[ind], this.startcp[ind-1]];
            } else if (mode == 1) {
                [this.cp[ind-1], this.cp[ind]] = [this.cp[ind], this.cp[ind-1]];
            }
            this.$forceUpdate();
        },

        movedown: function (ind, mode) {
            if (mode == 0) {
                if (ind == this.startcp.length-1) return;
                [this.startcp[ind], this.startcp[ind+1]] = [this.startcp[ind+1], this.startcp[ind]];
            } else if (mode == 1) {
                if (ind == this.cp.length-1) return;
                [this.cp[ind], this.cp[ind+1]] = [this.cp[ind+1], this.cp[ind]];
            }
            this.$forceUpdate();
        },

        deleteA: function(ind, mode) {
            if (mode == 0) {
                this.startcp.splice(ind,1)
            } else if (mode == 1) {
                this.cp.splice(ind,1)
            }
            this.$forceUpdate();
        },

        copyPrompt: function(prompt) {
            this.start = prompt['start']
            this.startcp = JSON.parse(prompt['initcheckpoints'])
            this.cp = JSON.parse(prompt['checkpoints'])
            this.seed = prompt['seed']
            this.$forceUpdate();
        }
    },

    mounted: function() {
        let input = document.getElementById("inputField");
        input.addEventListener("keyup", function(event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                document.getElementById("addInputToCPEnd").click();
            }
        });
    },

    template: (`
        <div>
            <div>
                <div class="input-group">
                    <label class="input-group-text" for="seedField">Seed:</label>
                    <input class="form-control" type="text" name="seedField" v-model="seed">
                </div>

                <div>
                    <div>Starting Article: {{start}}</div>
                    <div>Starting Checkpoints:
                        <ol>
                        <template v-for="(item, index) in startcp">
                            <li>{{item}}
                                <button v-on:click="moveup(index, 0)"><i class="bi bi-chevron-up"></i></button>
                                <button v-on:click="movedown(index, 0)"><i class="bi bi-chevron-down"></i></button>
                                <button v-on:click="deleteA(index, 0)"><i class="bi bi-trash"></i></button>
                            </li>
                        </template>
                        </ol>
                    </div>
                    <div>Reserve Checkpoints:
                        <ol>
                        <template v-for="(item, index) in cp">
                            <li>{{item}}
                                <button v-on:click="moveup(index, 1)"><i class="bi bi-chevron-up"></i></button>
                                <button v-on:click="movedown(index, 1)"><i class="bi bi-chevron-down"></i></button>
                                <button v-on:click="deleteA(index, 1)"><i class="bi bi-trash"></i></button>
                            </li>
                        </template>
                        </ol>
                    </div>
                </div>

                <div class="input-group">
                    <label class="input-group-text" for="inputField">Add checkpoint:</label>
                    <input class="form-control" type="text" name="inputField" id="inputField">
                </div>
                <div>
                    <button v-on:click="addArticle(0)">Set start</button>
                </div>
                <div>
                    <button v-on:click="addArticle(1)">Add article to starting checkpoints (end of list)</button>
                    <button v-on:click="addArticle(2)">Add article to starting checkpoints (start of list)</button>
                </div>
                <div>
                    <button v-on:click="addArticle(3)" id="addInputToCPEnd">Add article to checkpoints (end of list)</button>
                    <button v-on:click="addArticle(4)">Add article to checkpoints (start of list)</button>
                </div>
                <button id="genMarathonPromptButton" v-on:click="submitPrompt">Click to submit prompt</button>
            </div>
            <hr>
            <div id="generatedMarathonText"></div>
            <hr>
            <div class="row">
                <div class="col px-0"> <div class="card"> <div class="card-body">
                    <h4> Marathon prompts: </h4>
                    <ul>
                        <marathon-item
                            v-for="p in marathonprompts"
                            v-bind:prompt="p"
                            v-bind:key="p.prompt_id"
                            v-on:change="emit('reload-prompts')"
                            v-on:copy-prompt="copyPrompt(p)"
                        >
                        </marathon-item>
                    </ul>
                </div></div></div>
            </div>
        </div>
    `)
});




var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        unused: [],
        weeks: [],
        marathon: [],

        startPrompt: "",
        endPrompt: "",
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

            const marathonprompts = await (await fetchJson("/api/marathon/all")).json();

            this.marathon = marathonprompts;
        },

        async newPrompt(event) {

            const start = await getArticleTitle(this.startPrompt);
            if (!start) {
                alert(`Invalid article name "${this.startPrompt}"`);
                return;
            }

            const end = await getArticleTitle(this.endPrompt);
            if (!end) {
                alert(`Invalid article name "${this.endPrompt}"`);
                return;
            }

            const checkRes = await articleCheck(this.endPrompt);
            if ('warning' in checkRes) {
                alert(checkRes["warning"]);
                return;
            }

            try {
                const response = await fetchJson("/api/sprints/", "POST", {
                    "start": start,
                    "end": end
                })

            } catch (e) {
                console.log(e);
            }

            this.getPrompts();
        }

    } // End methods
}); // End vue