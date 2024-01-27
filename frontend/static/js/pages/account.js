import Vue from 'vue/dist/vue.esm.js';

import { fetchJson } from "../modules/fetch.js";
import { profileStatsTable } from "../modules/profileStats.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',

    components: {
        'profile-stats-table': profileStatsTable,
    },

    data: {
        username: "",
        loggedIn: false,
        emailConfirmed: false,
        feedbackMsg: '',
        confirmText: "Delete my account permanently!",
        tab:'',

    },

    created: async function() {
        if ("username" in serverData) {
            this.loggedIn = true;
            this.username = serverData["username"];
            this.isAdmin = serverData["admin"];
        } else {
            window.location.href = "/";  // redirect home if not logged in
        }

        this.getEmailConfirmed();
    },

    methods: {
        async handleLogout(event)
        {
            event.preventDefault();
            await fetch("/api/users/logout", {method : "POST"});
            window.location.href = "/";
        },

        async getEmailConfirmed(event)
        {
            const response = await fetch("/api/users/check_email_confirmation", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(serverData["username"])
            });

            this.emailConfirmed = await response.text();
        },

        async verifyEmail(event) {
            try {
                const response = await fetchJson("/api/users/confirm_email_request", 'POST');
                if (response.status === 200) {
                    alert("Email verification request has been sent. ");
                }
            } catch (e) {
                alert(e);
            }
        },

        async submitNewUsername(event) {

            if (document.getElementById("new-username").value != document.getElementById("new-username-check").value) {
                this.feedbackMsg = "Usernames do not match"
                return
            }


            const body = {
                'new_username' : document.getElementById("new-username").value
            };

            try {
                const response = await fetchJson("/api/users/change_username", 'POST', body);
                if (response.status === 200) {
                    window.location.reload();
                }
                this.feedbackMsg = await response.text()
            } catch (e) {
                console.log(e);
            }
        },

        async load(url) {
            window.location.href=url;
        },

        async deleteAccount(event) {

            if (document.getElementById("confirm-text").value != this.confirmText) {
                this.feedbackMsg = "Confirmation text does not match";
                return;
            }

            const body = {
                'username' : document.getElementById("deleteU-username").value
            };

            try {

                const response = await fetchJson("/api/users/delete_account", 'DELETE', body);
                if (response.status === 200) {
                    alert("Account has been deleted");
                    await fetch("/api/users/logout", {method : "POST"});
                    window.location.href = "/";
                } else {
                    this.feedbackMsg = await response.text()
                }
            } catch (e) {
                console.log(e);
            }
        }
    }

});
