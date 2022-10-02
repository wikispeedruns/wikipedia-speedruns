import { fetchJson } from "./fetch.js";

var quickPlaySuggestions = {

	data: function () {
        return {
            mostRecent: [{
                start: 'test', end: 'Test'
            }]
        }
	},

	methods: {

        async getMostRecent(num=5) {
            const response = await fetchJson(`/api/runs/most_recent?num=${num}` , "GET");
            const prompts = await response.json();
            data.mostRecent = prompts
        },
	},

	template: (`
        <div>
            <div style="width: 100%;">
                <div v-for='p in mostRecent'>
                    (start: {{p.start}}, end: {{p.end}})
                </div>
            </div>
        </div>
    `)
};

export {quickPlaySuggestions}
