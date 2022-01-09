import {fetchJson} from "./modules/fetch.js";
import {dateToIso} from "./modules/date.js";

Vue.component('prompt-item', {
    props: ['prompt'],

    methods: {
        async deletePrompt() {
            const prompts = await fetch("/api/prompts/" + this.prompt.prompt_id, {method: "DELETE"});
            this.$emit('change')
        }
    },

    template: (`
    <li>
        <strong>{{prompt.prompt_id}}</strong>: {{prompt.start}} -> {{prompt.end}} 
        <button v-on:click="deletePrompt" type="button" class="btn btn-default">
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
                "ranked": false,
            });

            if (response.status != 200) {
                alert(await response.text());
            } else {
                this.$emit('change')  // TODO reload just this box instead of triggering a full realead
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
            >
            </prompt-item>
        </ul>

        <form class="form-inline" v-on:submit.prevent="moveToDay">
            <div class="input-group input-group-sm mb-2">
                <input type="number" class="form-control" v-model="promptToAdd">
                <div class="input-group-append">
                    <button type="submit" class="btn btn-dark"> 
                        <i class="bi bi-arrow-right-square"></i> 
                    </button>
                </div>
            </div>
        </form>


    </div>
    `)
})


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        unused: [],
        public: [],
        weeks: [],

        toMakePublic: 0
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

            console.log(daysToPrompts)

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
                        "prompts": daysToPrompts[dateToIso(day)]
                    });

                    console.log(daysToPrompts[dateToIso(day)])
                    cur.setDate(cur.getDate() + 1);
                }
            }
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
        

    }
})
