import Vue from "vue/dist/vue.esm.js";

// TODO rules
import { fetchJson } from "../..//modules/fetch.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        name: "",
        desc: "",

        competitiveMode: false,
        requireAccount: false,
    },

    methods: {
        async handleSubmit() {
            let requestBody = {
                // TODO rules
                rules: {}
            }

            // See schema for rules
            requestBody.rules["hide_prompt_end"] = this.competitiveMode;
            requestBody.rules["restrict_leaderboard_access"] = this.competitiveMode;

            requestBody.rules["require_account"] = this.requireAccount;

            // Only add these fields if not empty
            if (this.name) requestBody["name"] = this.name;
            if (this.desc) requestBody["desc"] = this.desc;

            let resp = await fetchJson("/api/lobbys", "POST", requestBody);
            const lobby_id = (await resp.json())["lobby_id"];

            window.location.href = `/lobby/${lobby_id}`
        }
    }

});
