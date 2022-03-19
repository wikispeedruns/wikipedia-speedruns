import { fetchJson } from "./modules/fetch.js";
import { getPath } from "./modules/scraper.js";
import { getArticleTitle } from "./modules/wikipediaAPI/util.js";

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
    </li>`
    )
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
                this.$emit('move-prompt')  // TODO reload just this box instead of triggering a full realead
            }
        },
    },

    data: function () {
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
            this.path = await getPath(this.pathStart, this.pathEnd);
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
                const response = await fetchJson("/api/scraper/gen_prompts", 'POST', {
                    'N': 1
                })

                if (response.status != 200) {
                    // For user facing interface, do something other than this
                    alert(await response.text());
                    return;
                }

                const resp = await response.json()

                let prompt = {};

                prompt.start = resp['Prompts'][0][0];
                prompt.end = resp['Prompts'][0][1];
                prompt.path = await getPath(prompt.start, prompt.end);

                this.prompts.push(prompt);
            } catch(e) {
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




var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        unused: [],
        weeks: [],

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

                    const day =  new Date(cur);
                    this.weeks[i].days.push( {
                        "date": this.toISODate(day),
                        "prompts": nextDailys[this.toISODate(day)] || []
                    });

                    cur.setDate(cur.getDate() + 1);
                }
            }
        },

        async newPrompt(event) {

            const start = await getArticleTitle(this.startPrompt);
            if (!start) {
                alert(`Invalid article name "${this.startPrompt}"`);
            }

            const end = await getArticleTitle(this.endPrompt);
            if (!end) {
                alert(`Invalid article name "${this.endPrompt}"`);
            }

            try {
                const response = await fetchJson("/api/sprints/", "POST", {
                    "start": start,
                    "end": end
                })

            } catch(e) {
                console.log(e);
            }

            this.getPrompts();
        }

    } // End methods
}); // End vue



