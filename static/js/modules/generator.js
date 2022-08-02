import { getArticleTitle } from "./wikipediaAPI/util.js";
import { fetchJson } from "./fetch.js";

async function getGeneratedPrompt(difficulty, num)
{
    const response = await fetchJson(`/api/generator/prompt?difficulty=${difficulty}&num_articles=${num}` , "GET");
    const prompts = await response.json();

    // Load prompts simultaneously
    return await Promise.all(prompts.map(getArticleTitle));
}

var PromptGenerator = {

    props: {
        // Two way binding/v-model
        start: String,
        end: String
    },

	data: function () {
        return {
            logdifficulty: 3.5,
        }
	},

    computed: {
        difficulty() {
            return Math.round(Math.pow(10, this.logdifficulty))
        },

        approx_difficulty() {
            // Returns difficulty with 2 sig figs to give a sense of how many prompts you are choosing rom
            const rounding = Math.pow(10, Math.floor(this.logdifficulty));
            return Math.round(this.difficulty / rounding) * rounding;
        }
    },

	methods: {
        async generatePrompt() {
            const [start, end] = await getGeneratedPrompt(this.difficulty, 2);
            this.$emit('update:start', start);
            this.$emit('update:end', end);
        },
        async generateStart() {
            const [start] = await getGeneratedPrompt(this.difficulty, 1);
            this.$emit('update:start', start);

        },
        async generateEnd() {
            const [end] = await getGeneratedPrompt(this.difficulty, 1);
            this.$emit('update:end', end);
        }
	},

	template: (`
        <div>
            <div>
                Less Obscure <input type="range" min="2" max="5" v-model="logdifficulty" class="slider" step="0.1">More Obscure 
            </div> 
            <div>(Choosing from {{approx_difficulty}} articles)</div>

            <!-- expression for 1-100 scale {{Math.floor(33 * (logdifficulty - 2)) + 1}}-->

            <div class="my-2">
                <div class="btn-group">
                    <button class="btn btn-primary border-dark" v-on:click.prevent="generatePrompt"> Prompt </button>
                    <button class="btn btn-primary border-dark" v-on:click.prevent="generateStart"> Start </button>
                    <button class="btn btn-primary border-dark" v-on:click.prevent="generateEnd"> End </button>
                </div>
            </div>
            <p>
                <small><a href="/generator#about"> How does this work? </a></small>
            </p>
        </div>
    `)
};

export {PromptGenerator, getGeneratedPrompt}
