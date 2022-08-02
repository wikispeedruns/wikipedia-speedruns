
import { autocompleteInput } from "./modules/autocomplete.js";
import { PromptGenerator } from "./modules/generator.js"
import { getArticleTitle, articleCheck } from "/static/js/modules/wikipediaAPI/util.js";

var customPlay = {
    components: {
        'prompt-generator': PromptGenerator,
        'ac-input': autocompleteInput
    },

    data: function () {
        return {
            start: "", // The input article names
            end: "",

            startPrompt: "",  // The actual wikipedia article names that will be played
            endPrompt: "", 

            articleCheckMessage: ""
        }
	},

    methods: {

        async checkArticles() {
            this.articleCheckMessage = "";
            
            if(this.start == "" || this.end == ""){
                this.articleCheckMessage = "Prompt is currently empty";
                return;
            }
            this.startPrompt = await getArticleTitle(this.start);
            if (this.startPrompt === null) {
                this.articleCheckMessage = `"${this.start}" is not a Wikipedia article`;
                return;
            }

            this.endPrompt = await getArticleTitle(this.end);
            if (this.endPrompt === null) {
                this.articleCheckMessage = `"${this.end}" is not a Wikipedia article`;
                return;
            }

            const checkRes = await articleCheck(this.endPrompt);
            if ('warning' in checkRes) {
                this.articleCheckMessage = checkRes["warning"];
                return;
            }
        },

        async play() {

            await this.checkArticles();
            if(this.articleCheckMessage != "") return;

            console.log(`${this.startPrompt} -> ${this.endPrompt}`);
            
            const start_param = encodeURIComponent(this.startPrompt).replace('%2F', '%252F');
            const end_param = encodeURIComponent(this.endPrompt).replace('%2F', '%252F');
            window.location.replace(`/play/${start_param}/${end_param}`);
        }
	},

    template: (`
        <div>
            <div class="col-md-4 col-sm-6">
                <ac-input :text.sync="start" placeholder="Start Article"></ac-input>
                <ac-input :text.sync="end" placeholder="End Article"></ac-input>
            </div>

            <details class="mb-4">
                <summary> Generate Random Articles </summary>

                <prompt-generator
                    v-bind:start.sync="start"
                    v-bind:end.sync="end"
                ></prompt-generator>

            </details>

            <p class="text-danger">{{articleCheckMessage}}</p>

            <button class="btn btn-primary" v-on:click.prevent="play"> Play </button>
        </div>
    `)
};

export { customPlay }