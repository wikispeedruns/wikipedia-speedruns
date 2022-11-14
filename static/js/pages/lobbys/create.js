import Vue from "vue/dist/vue.esm.js";

// TODO rules
import { fetchJson } from "../..//modules/fetch.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        name: "",
        desc: "",
    },

    methods: {
        async handleSubmit() {
            let requestBody = {
                // TODO rules
                rules: {}
            }

            // Only add these fields if not empty
            if (this.name) requestBody["name"] = this.name;
            if (this.desc) requestBody["desc"] = this.desc;

            let resp = await fetchJson("/api/lobbys", "POST", requestBody);
            const lobby_id = (await resp.json())["lobby_id"];

            window.location.href = `/lobby/${lobby_id}`
        }
    }

});
