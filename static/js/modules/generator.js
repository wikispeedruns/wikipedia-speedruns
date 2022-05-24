import { getArticleTitle } from "./wikipediaAPI/util.js";
import { fetchJson } from "./fetch.js";

async function getGeneratedPrompt(difficulty)
{
    const response = await fetchJson(`/api/generator/prompt?difficulty=${difficulty}` , "GET");
    const prompt = await response.json();


    // Load start and end simultaneously
    let start, end;
    await Promise.all([
        getArticleTitle(prompt["start"]).then((title) => {start = title}),
        getArticleTitle(prompt["end"]).then((title) => {end = title})
    ]);

    return {start, end};
}

var PromptGenerator = {

	data: function () {
        return {
            start: "Start Article",
            end: "End Article",
            logdifficulty: 3,
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

            const prompt = await getGeneratedPrompt(this.difficulty);
            this.start = prompt["start"];
            this.end = prompt["end"];
        }
	},

	template: (`
        <div class="card">
        <div class="card-body">

            <div class="row" >
                <div class="col-sm-6 py-3 text-center">
                    <h4>{{start}} </h4>
                </div>

                <div class="col-sm-6 py-3 text-center" >
                    <h4>{{end}} </h4>
                </div>
            </div>

            <div class="row">

                <div class="col-sm-6">
                    <input type="range" min="2" max="5" v-model="logdifficulty" class="slider" step="0.1">
                    <p>Selecting from the {{approx_difficulty}} most reachable articles</p>

                    <button class="btn btn-primary" v-on:click="generatePrompt"> Click to generate a prompt! </button>
                </div>



            </div>


        </div>
        </div>
    `)
};

export {PromptGenerator, getGeneratedPrompt}