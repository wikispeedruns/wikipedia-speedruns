import { fetchJson } from "./modules/fetch.js";
import { dateToIso } from "./modules/date.js";

import { getPath } from "./modules/scraper.js";

Vue.component('prompt-item', {
    props: ['prompt'],

    data: function() {
        return {
            ratedChecked: this.prompt.rated
        }
    },

    methods: {

        async deletePrompt() {
            const resp = await fetchJson("/api/prompts/" + this.prompt.prompt_id, "DELETE");
            
            if (resp.status == 200) this.$emit('delete-prompt')
            else alert(await resp.text())
        },

        async changeRated() {
            const resp = await fetchJson("/api/prompts/" + this.prompt.prompt_id + "/type", "PATCH", {
                "type": "daily",
                "date": this.prompt.date,
                "rated": this.ratedChecked,
            });

            if (resp.status != 200) alert(await resp.text())
        }
    },

    template: (`
    <li>
        <strong>{{prompt.prompt_id}}</strong>: {{prompt.start}} -> {{prompt.end}} 

        <input type="checkbox" v-if="prompt.type==='daily'" v-model="ratedChecked" v-on:change="changeRated">

        <button v-on:click="deletePrompt" type="button" class="btn btn-default">
            <i class="bi bi-trash"></i>
        </button>
    </li>`
    )
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
    },

    template: (`
    <li>
        <strong>{{prompt.prompt_id}}</strong>: {{prompt.start}} 
        <div>{{prompt.initcheckpoints}}</div>
        <div>{{prompt.checkpoints}}</div>
        <button v-on:click="deletePrompt" type="button" class="btn btn-default" >
            <i class="bi bi-trash"></i>
        </button>
    </li>`
    )
});


// TODO maybe these should load the date stuff themselves (At least on update)
Vue.component('daily-item', {
    props: ['day'],

    methods: {
        async moveToDay() {
            const response = await fetchJson("/api/prompts/" + this.promptToAdd + "/type", "PATCH", {
                "type": "daily",
                "date": this.day.dateIso,
                "rated": false,
            });

            if (response.status != 200) {
                alert(await response.text());
            } else {
                this.$emit('move-prompt')  // TODO reload just this box instead of triggering a full realead
            }
        },
        dateToIso,
    },

    data: function () {
        return {
            promptToAdd: 0
        }
    },

    template: (`
    <div>
        <strong v-if="day.dateIso === dateToIso(new Date())">
            <p>{{day.dateIso.substring(5)}}</p>
        </strong>
        <p v-else>{{day.dateIso.substring(5)}}</p>


        <ul class="ps-3 my-0">
            <prompt-item 
                v-for="p in day.prompts"
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



Vue.component('marathon-generator', {
    data: function() {
        return {
            start: "China",
            cp1: "United States",
            cp2: "Nickle",
            cp3: "Road",
            cp4: "DNA",
            cp5: "Clay",
            seed: "123456",
            nbucket: "5",
            nbatch: "5",
            nperbatch: "10"
        }
    },


    methods: {
        genMarathonPrompt: async function () {
            try {
                console.log(this.$data)

                const response = await fetchJson("/api/marathon/add/", 'POST', this.$data)
        
                if (response.status != 200) {
                    // For user facing interface, do something other than this
                    alert(await response.text());
                    return;
                }

                const resp = await response.json()

                console.log(resp)
                
            } catch(e) {
                console.log(e);
            }
        }
    },

    template: (`
        <div>
            <div class="input-group">
                <label class="input-group-text" for="startField">Start Article:</label>
                <input class="form-control" type="text" name="startField" v-model="start">
            </div>
            <div class="input-group">
                <label class="input-group-text" for="cp1Field">1st CP:</label>
                <input class="form-control" type="text" name="cp1Field" v-model="cp1">
            </div>
            <div class="input-group">
                <label class="input-group-text" for="cp2Field">2nd CP:</label>
                <input class="form-control" type="text" name="cp2Field" v-model="cp2">
            </div>
            <div class="input-group">
                <label class="input-group-text" for="cp3Field">3rd CP:</label>
                <input class="form-control" type="text" name="cp3Field" v-model="cp3">
            </div>
            <div class="input-group">
                <label class="input-group-text" for="cp4Field">4th CP:</label>
                <input class="form-control" type="text" name="cp4Field" v-model="cp4">
            </div>
            <div class="input-group">
                <label class="input-group-text" for="cp5Field">5th CP:</label>
                <input class="form-control" type="text" name="cp5Field" v-model="cp5">
            </div>
            <div class="input-group">
                <label class="input-group-text" for="seedField">Seed:</label>
                <input class="form-control" type="text" name="seedField" v-model="seed">
            </div>
            <div class="input-group">
                <label class="input-group-text form-control" for="nbatch">N-Bucket:</label>
                <input class="form-control" type="text" name="nbatch" v-model="nbatch">
                <label class="input-group-text form-control" for="nbucket">N-Batch:</label>
                <input class="form-control" type="text" name="nbucket" v-model="nbucket">
                <label class="input-group-text form-control" for="nperbatch">N-PerBatch:</label>
                <input class="form-control" type="text" name="nperbatch" v-model="nperbatch">
            </div>
            <button id="genMarathonPromptButton" v-on:click="genMarathonPrompt">Click to generate and submit a random marathon prompt</button>
        </div>
        <hr>
    `)

});




var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        unused: [],
        public: [],
        weeks: [],
        marathon: [],

        toMakePublic: 0,
    },

    created: async function() {
        await this.getPrompts();
    },
    
    methods: {
        async getPrompts() {
            const prompts = await (await fetchJson("/api/prompts/all")).json();
            
            this.unused = prompts.filter(p => p["type"] === "unused");
            this.public = prompts.filter(p => p["type"] === "public");
            
            
            let daily = prompts.filter(p =>  p["type"] === "daily");
            
            let daysToPrompts = {};

            daily.forEach((p) => {
                if (!daysToPrompts[p["date"]]) {
                    daysToPrompts[p["date"]] = [];
                }
                daysToPrompts[p["date"]].push(p);
            });


            let today = new Date();
            let cur = new Date(today);

            // Change cur to first day of this week
            cur.setDate(cur.getDate() - cur.getDay());

            this.weeks = [];
            for (let i = 0; i < 3; i++) {
                this.weeks.push([]);
                for (let j = 0; j < 7; j++) {

                    const day =  new Date(cur);
                    this.weeks[i].push( {
                        "date": day,
                        "dateIso": dateToIso(day),
                        "prompts": daysToPrompts[dateToIso(day)] || []
                    });

                    cur.setDate(cur.getDate() + 1);
                }
            }

            const marathonprompts = await (await fetchJson("/api/marathon/all")).json();

            this.marathon = marathonprompts;
        },


        async makePublic() {
            const response = await fetchJson("/api/prompts/" + this.toMakePublic + "/type", "PATCH", {
                "type": "public"
            });

            if (response.status != 200) {
                alert(await response.text());
            } else {
                this.getPrompts();
            }

        },


        async newPrompt(event) {
    
            let reqBody = {};
        
            const resp = await fetch(
                `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("start").value}`,
                {
                    mode: "cors"
                }
            )
            const body = await resp.json()
        
            reqBody["start"] = body["parse"]["title"];
        
        
            const resp1 = await fetch(
                `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("end").value}`,
                {
                    mode: "cors"
                }
            )
            const body1 = await resp1.json()
        
            reqBody["end"] = body1["parse"]["title"];
        
            try {
                const response = await fetch("/api/prompts/", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(reqBody)
                })
        
            } catch(e) {
                console.log(e);
            }
        
            this.getPrompts();
        }

    } // End methods
}); // End vue



