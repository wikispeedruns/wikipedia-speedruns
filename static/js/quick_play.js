
import { PromptGenerator } from "./modules/generator.js"
import { getArticleTitle, articleCheck } from "/static/js/modules/wikipediaAPI/util.js";

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'prompt-generator': PromptGenerator
    },

    data: {

        start: "", // The input article names
        end: "",

        startPrompt: "",  // The actual wikipedia article names that will be played
        endPrompt: "", 

        articleCheckMessage: ""
    },

    methods: {

        playRandom() {
            // const difficulty = this.getDifficulty(default_difficulty);
            // const [start, end] = await getGeneratedPrompt(difficulty, 2);
            // this.start = start;
            // this.end = end;

            this.start = "Big Bang";
            this.end = "Australia (continent)";

            this.play();
        },

        async checkArticles() {
            this.articleCheckMessage = "";

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

            const checkRes = await articleCheck(this.end);
            if ('warning' in checkRes) {
                this.articleCheckMessage = checkRes["warning"];
                return;
            }
        },

        async play() {

            await this.checkArticles();
            if(this.articleCheckMessage != "") return;

            const start_param = encodeURIComponent(this.start);
            const end_param = encodeURIComponent(this.end);
            window.location.replace(`/play/${start_param}/${end_param}`);
        },
	}

});