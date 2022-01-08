import {fetchJson} from "./modules/fetch.js"

Vue.component('prompt-item', {
    // The todo-item component now accepts a
    // "prop", which is like a custom attribute.
    // This prop is called todo.
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
})

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        unused: [],
        public: [],
        daily: [],
    },

    created: async function() {
        await this.getPrompts();
    },
    
    methods: {
        async getPrompts() {
            const prompts = await fetchJson("/api/prompts/all");
            
            this.unused = prompts.filter(p => p["type"] === "unused")
            this.public = prompts.filter(p => p["type"] === "public")
            this.daily = prompts.filter(p => p["type"] === "daily")
        },

        async onsubmit(event) {
        
            reqBody = {};
        
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
        
                console.log(response);
            } catch(e) {
                console.log(e);
            }
        
            getPrompts();
        }
        

    }
})
