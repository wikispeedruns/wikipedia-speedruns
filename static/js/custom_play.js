
import { autocompleteInput } from "./modules/autocomplete.js";
import { PromptGenerator } from "./modules/generator.js"
import { checkArticles } from "/static/js/modules/wikipediaAPI/util.js";

var customPlay = {
    components: {
        'prompt-generator': PromptGenerator,
        'ac-input': autocompleteInput
    },

    data: function () {
        return {
            start: "", // The input article names
            end: "",

            articleCheckMessage: ""
        }
	},

    methods: {

        async generateRndPrompt(prompt) {
            [this[prompt]] = await this.$refs.pg.generatePrompt();
        },

        play(start, end) {
            const start_param = encodeURIComponent(start).replaceAll('%2F', '%252F');
            const end_param = encodeURIComponent(end).replaceAll('%2F', '%252F');
            window.location.replace(`/play/quick_play?prompt_start=${start_param}&prompt_end=${end_param}`);
        },

        async playCustom() {
            this.articleCheckMessage = "";
            const resp = await checkArticles(this.start, this.end);
            if(resp.err) {
                this.articleCheckMessage = resp.err;
                return;
            }

            this.play(resp.body.start, resp.body.end);
        },

        async playRandom() {
            let resp;
            do {
                const [start, end] = await this.$refs.pg.generatePrompt(2);
                console.log("start: " + start + " end: " + end);
                resp = await checkArticles(start, end);
            } while (resp.err);
            
            this.play(resp.body.start, resp.body.end);
        },
	},

    template: (`
        <div>
            <div class="row">
                <div class="col-sm mb-2 mb-sm-0">
                    <div class="input-group flex-nowrap">
                        <ac-input :text.sync="start" placeholder="Start Article"></ac-input>
                        <button type="button" class="btn border quick-play" @click="generateRndPrompt('start')">
                            <i class="bi bi-shuffle"></i>
                        </button>
                    </div>
                </div>
                <div class="col-sm">
                    <div class="input-group flex-nowrap">
                        <ac-input :text.sync="end" placeholder="End Article"></ac-input>
                        <button type="button" class="btn border quick-play" @click="generateRndPrompt('end')">
                            <i class="bi bi-shuffle"></i>
                        </button>
                    </div>
                </div>
                <p v-if="articleCheckMessage" class="text-danger mb-0">{{articleCheckMessage}}</p>
            </div>

            <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                <button type="button" class="btn quick-play" v-on:click="playCustom">Play Now</button>
                <button type="button" class="btn quick-play" v-on:click="playRandom">I'm Feeling Lucky</button>
            </div>

            <details>
                <summary>Random Article Generator Settings</summary>
                <prompt-generator ref="pg"></prompt-generator>
            </details>
        </div>
    `)
};

export { customPlay }