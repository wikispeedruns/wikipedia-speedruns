import { getArticleTitle } from "../wikipediaAPI/util.js";
import { fetchJson } from "../fetch.js";
import { PromptGenerator } from "../generator.js"
import { AutocompleteInput } from "../autocomplete.js";

var MarathonBuilder = {

    props: ['admin'],

    components: {
        'prompt-generator': PromptGenerator,
        'ac-input': AutocompleteInput
    },

    data: function() {
        return {
            start: "United States",
            startcp: [],
            cp: [],
            seed: "0",
            anonymous: true,
            placeholder: "",
            articleCheckMessage: "",
            language: "en",
        }
    },

    methods: {

        async generateRndPrompt(prompt) {
            [this[prompt]] = await this.$refs.pg.generatePrompt();
        },

        submitPrompt: async function() {
            
            if (this.startcp.length != 5) throw new Error("Need 5 starting checkpoints");
            if (this.cp.length < 40) throw new Error("Need 40+ checkpoints");

            try {
                if (this.admin) {
                    await this.submitAsAdmin();
                } else {
                    await this.submitAsCmty();
                }
            } catch (e) {
                this.articleCheckMessage = e
                console.log(e);
            }
        },

        submitAsAdmin: async function() {
            const response = await fetchJson("/api/marathon/add/", 'POST', {'data': this.$data })
            if (response.status != 200) {
                // For user facing interface, do something other than this
                alert(await response.text());
                return;
            }
            this.articleCheckMessage = "Prompt submit success. Refresh to see recently added prompt"
        },

        submitAsCmty: async function() {
            const response = await fetchJson("/api/community_prompts/submit_marathon_prompt", 'POST', {
                'data': this.$data,
                "anonymous": this.anonymous }
            )
            if (response.status != 200) {
                // For user facing interface, do something other than this
                alert(await response.text());
                return;
            }
            this.articleCheckMessage = "Prompt submitted for approval"
        },

        addArticle: async function(mode) {
            if (this.placeholder.length < 1) return;

            let a = await getArticleTitle(this.placeholder)

            if (this.cp.includes(a) || this.startcp.includes(a) || this.start == a ) {
                this.articleCheckMessage = "Article already exists"
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
                this.placeholder = String(this.cp.length)
                await this.addArticle(3)
            }
            while (this.startcp.length < 5) {
                this.placeholder = String(this.startcp.length + 40)
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
        <div class="row">
            <div class="col-sm">
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

            <div class="col-sm">
                <div class="row">
                    <div class="col-sm mb-2">
                        <div class="input-group flex-nowrap">
                            <ac-input :text.sync="placeholder" :lang="language" placeholder="Article" id="inputField"></ac-input>
                            <button type="button" class="btn border quick-play" @click="generateRndPrompt('placeholder')">
                                <i class="bi bi-shuffle"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-sm mb-2">
                        <div class="input-group flex-nowrap">
                            <input class="form-control" type="text" name="seedField" v-model="seed">
                        </div>
                    </div>
                    <p v-if="articleCheckMessage" class="text-danger mb-0">{{articleCheckMessage}}</p>
                </div>

                <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                    <button v-on:click="addArticle(0)">Set start</button>
                </div>

                <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                    <button v-on:click="addArticle(1)">Add to END of starting checkpoints</button>
                    <button v-on:click="addArticle(2)">Add to START of starting checkpoints</button>
                </div>

                <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                    <button v-on:click="addArticle(3)" id="addInputToCPEnd">Add to END of checkpoints</button>
                    <button v-on:click="addArticle(4)">Add to START of checkpoints</button>
                </div>
                
                <div class="form-check" v-if="!admin">
                    <label class="form-check-label">
                        <input class="form-check-input" type="checkbox" v-model="anonymous">
                        Anonymous Submission
                    </label>
                </div>

                <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                    <button type="button" class="btn quick-play" v-on:click="submitPrompt">Submit</button>
                    <button type="button" class="btn quick-play" v-on:click="loadGeneric">Load Example</button>
                </div>

                <details>
                    <summary>Random Article Generator Settings</summary>
                    <prompt-generator ref="pg"></prompt-generator>
                </details>
            </div>
        </div>
    `)
};

export {MarathonBuilder}