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

            let start_title = resp.body.start
            let end_title = resp.body.end

            try {
                const check_res = await this.checkDuplicates(start_title, end_title);
                if (check_res[0] != 'none') {
                    var b = "This prompt is already an active prompt, in the prompt queue, or waiting for approval. "
                    if (!this.admin || (this.admin && !confirm(b + " Do you want to submit it anyway?"))) {
                        this.articleCheckMessage = b + " Please try a different prompt."
                        return;
                    } 
                } 

                if (this.admin) {
                    await this.submitAsAdmin(start_title, end_title);
                    this.articleCheckMessage = "Prompt submit success. "
                } else {
                    await this.submitAsCmty(start_title, end_title);
                    this.articleCheckMessage = "Prompt submitted for approval!"
                }

                this.$emit("refreshprompts")

                this.start = ""
                this.end = ""
            } catch (e) {
                console.log(e);
            }
        },

        swapPrompts() {
            var temp = this.start;
            this.start = this.end;
            this.end = temp;
        },

        async checkDuplicates(start, end) {
            const response = await fetchJson("/api/sprints/check_duplicate", "POST", {
                "start": start,
                "end": end
            })
            return await response.json()
        },

        async submitAsAdmin(start, end) {
            const response = await fetchJson("/api/sprints/", "POST", {
                "start": start,
                "end": end
            })
        },
        
        async submitAsCmty(start, end) {
            const response = await fetchJson("/api/community_prompts/submit_sprint_prompt", "POST", {
                "start": start,
                "end": end,
                "anonymous": this.anonymous
            })
        }
	},

    template: (`
        <div>
            <div class="row">
                <div class="col-md-5 mb-2">
                    <div class="input-group flex-nowrap">
                        <ac-input :text.sync="start" :lang="language" placeholder="Start Article"></ac-input>
                        <button type="button" class="btn border quick-play" @click="generateRndPrompt('start')">
                            <i class="bi bi-shuffle"></i>
                        </button>
                    </div>
                </div>
                <div class="col-auto px-0 mb-2 d-none d-md-block">
                    <button type="button" class="btn border quick-play mx-2" style="height:100%" @click="swapPrompts">
                        <i class="bi bi-arrow-left-right"></i>
                    </button>
                </div>
                <div class="col mb-2">
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

            <details class="my-2" v-show="!admin">
                <summary><strong>Prompt building tips: Sprints</strong></summary>
                <p>Here are some tips for building a good sprint prompt - with a higher likelihood of admin approval</p>
                <ol>
                <li>
                    <strong
                    >A good prompt should be challenging, but still very much
                    possible.</strong
                    >
                    Have you ever played a prompt that you KNEW you could get to,
                    but you still had to think about how to get there? That's a good
                    sprint prompt.
                </li>
                <li>
                    <strong>A good end article shouldn't be too niche.</strong> The
                    average player should be able to understand what the end article
                    is directly from the article title or the article summary.
                </li>
                <li>
                    Starting articles can be more specific, as long as there are
                    routes for reaching a more generic "hub" article, such as
                    "United States".
                </li>
                <li>
                    Avoid using countries as end articles, as they are often too
                    easy to get to. Try adding another layer or two of separation!
                </li>
                <li>
                    Try out a prompt in custom play to get a sense of how a prompt
                    could play out!
                </li>
                </ol>
            </details>
        </div>
    `)
};

export { SprintBuilder }
