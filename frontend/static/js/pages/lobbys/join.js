import Vue from "vue/dist/vue.esm.js";

import { fetchJson } from "../../modules/fetch.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        name: "",
        passcode: "",

        lobby_id: serverData["lobby_id"],
        user_id: serverData["user_id"],
        username: serverData["username"],

        message:""
    },

    methods: {
        async handleJoin() {
            // Only add these fields if not empty
            this.message = "";

            const requestBody = {
                "passcode": this.passcode
            };

            console.log(this.username);

            if (!this.username) {
                requestBody["name"] = this.name;
            }

            let resp = await fetchJson(`/api/lobbys/${this.lobby_id}/join`, "POST", requestBody);

            if (resp.status === 401 || resp.status === 404) {
                this.message = await resp.text();
            } else if (resp.status == 200) {
                window.location.href = `/lobby/${this.lobby_id}`;
            } else {
                this.message = "Error joining lobby";
            }
        }
    }

});
