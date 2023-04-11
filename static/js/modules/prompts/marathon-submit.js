import { getArticleTitle } from "../wikipediaAPI/util.js";
import { fetchJson } from "../fetch.js";

var MarathonBuilder = {

    props: [
        'admin'
    ],

    data: function() {
        return {
            start: "United States",
            startcp: [],
            cp: [],
            seed: "0",
            anonymous: true
        }
    },

    methods: {
        submitPrompt: async function() {
            
            if (this.startcp.length != 5) throw new Error("Need 5 starting checkpoints");
            if (this.cp.length < 40) throw new Error("Need 40+ checkpoints");

            if (this.admin) {
                await this.submitAsAdmin();
            } else {
                await this.submitAsCmty();
            }
        },

        submitAsAdmin: async function() {
            try {
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

        submitAsCmty: async function() {
            try {
                const response = await fetchJson("/api/community_prompts/submit_marathon_prompt", 'POST', {
                    'data': this.$data,
                    "anonymous": this.anonymous }
                )
                if (response.status != 200) {
                    // For user facing interface, do something other than this
                    alert(await response.text());
                    return;
                }
                document.getElementById("generatedMarathonText").innerHTML = "Prompt submitted for approval"
            } catch (e) {
                document.getElementById("generatedMarathonText").innerHTML = e
                console.log(e);
            }
        },

        addArticle: async function(mode) {
            if (document.getElementById("inputField").value.length < 1) return;

            let a = await getArticleTitle(document.getElementById("inputField").value)

            if (this.cp.includes(a) || this.startcp.includes(a) || this.start == a ) {
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

        loadGeneric: async function() {
            while (this.cp.length < 40) {
                document.getElementById("inputField").value = String(this.cp.length)
                await this.addArticle(3)
            }
            while (this.startcp.length < 5) {
                document.getElementById("inputField").value = String(this.startcp.length + 40)
                await this.addArticle(1)
            }
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
            <div v-if="admin">submitting as admin</div>
            <div v-else>submitting as cmty</div>
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
                <hr>
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
                <div>
                    <button id="genMarathonPromptButton" v-on:click="submitPrompt">Click to submit prompt</button>
                    <button id="loadgeneric" v-on:click="loadGeneric">Load Generic</button>
                </div>
                
                <form id="marathon" v-if="!admin">
                    <input type="checkbox" id="anony" name="anony" v-model="anonymous">
                    <label for="anony">Anonymous Submission</label>
                </form>
            </div>
            <hr>
            <div id="generatedMarathonText"></div>
        </div>
    `)
};

export {MarathonBuilder}