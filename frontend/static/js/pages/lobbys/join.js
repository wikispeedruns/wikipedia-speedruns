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

    mounted: function () {
        this.retrievePasscode();
    },

    methods: {
        // retrievePasscode attempts to retrieve the passcode from the url parameters
        retrievePasscode() {

            console.log('retrievePasscode')
            // use URLSearchParams instead of Vue Router because we are using Vue in a Multi-Page application
            // setup rather than the standard Single-Page application
            const urlParams = new URLSearchParams(window.location.search);

            // str if exists, else null
            const passcode = urlParams.get('passcode');

            if (passcode != null) {
                this.passcode = passcode;
            }
        },
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
