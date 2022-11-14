import { fetchJson } from "./fetch.js";

var quickPlaySuggestions = {

	data: function () {
        return {
            suggested: []
        }
	},

    created: async function () {
        await this.getSuggestions();
    },

	methods: {

        async getSuggestions(num=5) {
            const response = await fetchJson(`/api/quick_run/suggested?num=${num}` , "GET");
            const prompts = await response.json();
            this.suggested = prompts
        },
	},

	template: (`
        <div>
            <div class="container" style="width: 100%;">
                <h6>Here's what other players have been playing recently: </h6>
                <div class="row" v-for='p in suggested'>
                    <div class="col">
                        {{p.prompt_start}} <span><i class="bi bi-arrow-right-short"></i></span> {{p.prompt_end}}
                    </div>
                    <div class="col">
                        <a v-bind:href="'/play/quick_play?prompt_start=' + p.prompt_start + '&prompt_end='+ p.prompt_end">Play</a>
                    </div>
                </div>
            </div>
        </div>
    `)
};

export {quickPlaySuggestions}
