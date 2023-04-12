import { AutocompleteInput } from "../autocomplete.js";
import { PromptGenerator } from "../generator.js"
import { checkArticles } from "../wikipediaAPI/util.js";
import { fetchJson } from "../fetch.js";

var SprintBuilder = {

    props: ['admin'],

    components: {
        'prompt-generator': PromptGenerator,
        'ac-input': AutocompleteInput
    },

    data: function () {
        return {
            start: "", // The input article names
            end: "",
            anonymous: true,
            articleCheckMessage: "",
            language: "en",
        }
	},

    methods: {

        async generateRndPrompt(prompt) {
            [this[prompt]] = await this.$refs.pg.generatePrompt();
        },

        async submitPrompt() {

            this.articleCheckMessage = "";
            const resp = await checkArticles(this.start, this.end);
            if(resp.err) {
                this.articleCheckMessage = resp.err;
                return;
            }

            try {
                if (this.admin) {
                    await this.submitAsAdmin();
                } else {
                    await this.submitAsCmty();
                }
            } catch (e) {
                console.log(e);
            }

            this.$emit("refreshprompts")
        },

        async submitAsAdmin() {
            const response = await fetchJson("/api/sprints/", "POST", {
                "start": this.start,
                "end": this.end
            })
        },
        
        async submitAsCmty() {
            const response = await fetchJson("/api/community_prompts/submit_sprint_prompt", "POST", {
                "start": this.start,
                "end": this.end,
                "anonymous": this.anonymous
            })
        }
	},

    template: (`
        <div>
            <div class="row">
                <div class="col-md mb-2">
                    <div class="input-group flex-nowrap">
                        <ac-input :text.sync="start" :lang="language" placeholder="Start Article"></ac-input>
                        <button type="button" class="btn border quick-play" @click="generateRndPrompt('start')">
                            <i class="bi bi-shuffle"></i>
                        </button>
                    </div>
                </div>
                <div class="col-md mb-2">
                    <div class="input-group flex-nowrap">
                        <ac-input :text.sync="end" :lang="language" placeholder="End Article"></ac-input>
                        <button type="button" class="btn border quick-play" @click="generateRndPrompt('end')">
                            <i class="bi bi-shuffle"></i>
                        </button>
                    </div>
                </div>
                <p v-if="articleCheckMessage" class="text-danger mb-0">{{articleCheckMessage}}</p>
            </div>

            <div class="form-check" v-if="!admin">
                <label class="form-check-label">
                    <input class="form-check-input" type="checkbox" v-model="anonymous">
                    Anonymous Submission
                </label>
            </div>

            <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                <button type="button" class="btn quick-play" v-on:click="submitPrompt">Submit</button>
            </div>

            <details>
                <summary>Random Article Generator Settings</summary>
                <prompt-generator ref="pg"></prompt-generator>
            </details>
        </div>
    `)
};

export { SprintBuilder }
