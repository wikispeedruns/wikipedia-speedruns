import { AutocompleteInput } from "./autocomplete.js";
import { PromptGenerator } from "./generator.js"
import { checkArticles, getSupportedLanguages, getRandomArticle } from "./wikipediaAPI/util.js";

var CustomPlay = {
    components: {
        'prompt-generator': PromptGenerator,
        'ac-input': AutocompleteInput
    },

    data: function () {
        return {
            start: "", // The input article names
            end: "",

            articleCheckMessage: "",

            scroll: null,

            language: "en",
            languages: [],
        }
	},

    mounted() {
        this.getLanguages();
    },

    methods: {

        async getLanguages() {
            this.languages = await getSupportedLanguages();
        },

        async generateRndPrompt(prompt) {
            if (this.language === 'en') {
                [this[prompt]] = await this.$refs.pg.generatePrompt();
            } else {
                this[prompt] = await getRandomArticle(this.language);
            }
        },

        play(start, end, lang) {
            window.location.assign(`/play/quick_play?prompt_start=${start}&prompt_end=${end}&lang=${lang}${this.scroll ? '&scroll=1' : ''}`);
        },

        async playCustom() {
            this.articleCheckMessage = "";
            const resp = await checkArticles(this.start, this.end, this.language);
            if(resp.err) {
                this.articleCheckMessage = resp.err;
                return;
            }

            this.play(resp.body.start, resp.body.end, resp.body.lang);
        },

        async playRandom() {
            let resp;
            do {
                let start, end;
                if (this.language === 'en') {
                    [start, end] = await this.$refs.pg.generatePrompt(2);
                } else {
                    start = await getRandomArticle(this.language);
                    end = await getRandomArticle(this.language);
                }

                console.log("start: " + start + " end: " + end);
                resp = await checkArticles(start, end, this.language);
            } while (resp.err);

            this.play(resp.body.start, resp.body.end, resp.body.lang);
        },
	},

    template: (`
        <div>
            <div class="row">
                <div class="col-md-2 mb-2">
                    <select class="form-select" v-model="language">
                        <option selected value="en"> English (en) </option>
                        <option v-for="lang in languages" v-bind:value="lang.code">{{ lang.name }} ({{lang.code}})</option>
                    </select>
                </div>
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

            <div class="form-check">
                <label class="form-check-label">
                    <input class="form-check-input" type="checkbox" v-model="scroll">
                    Enable auto-scrolling
                </label>
            </div>

            <div class="gap-2 d-flex justify-content-center justify-content-md-start my-3">
                <button type="button" class="btn quick-play" v-on:click="playCustom">Play Now</button>
                <button type="button" class="btn quick-play" v-on:click="playRandom">I'm Feeling Lucky</button>
            </div>

            <details v-show="language === 'en'">
                <summary>Random Article Generator Settings</summary>
                <prompt-generator ref="pg"></prompt-generator>
            </details>
        </div>
    `)
};

export { CustomPlay }
