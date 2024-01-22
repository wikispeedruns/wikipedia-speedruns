import { getArticleTitle } from "./wikipediaAPI/util.js";
import { fetchJson } from "./fetch.js";

async function getGeneratedPrompt(difficulty=10000, num=1) {
    const response = await fetchJson(`/api/generator/prompt?difficulty=${difficulty}&num_articles=${num}` , "GET");
    const prompts = await response.json();

    // Load prompts simultaneously
    return await Promise.all(prompts.map(prompt => getArticleTitle(prompt)));
}

var PromptGenerator = {

	data: function () {
        return {
            logDifficulty: 3.5,
        }
	},

    computed: {
        difficulty() {
            const diff = Math.round(Math.pow(10, this.logDifficulty));
            const norm = Math.pow(10, Math.floor(this.logDifficulty));
            return Math.round(diff / norm) * norm;
        },
    },

	methods: {
        async generatePrompt(num=1) {
            return await getGeneratedPrompt(this.difficulty, num);
        },
	},

	template: (`
        <div>
            <label class="form-label" style="width: 100%;">
                Sample size:
                <input type="range" min="2" max="5" step="0.1" v-model="logDifficulty" class="form-range">
                Sampling from {{difficulty}} most popular articles
            </label>
        </div>
    `)
};

export {PromptGenerator, getGeneratedPrompt}
