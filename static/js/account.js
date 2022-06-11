import { serverData } from "./modules/serverData.js";
import { fetchJson } from "./modules/fetch.js";
import { profileStatsTable } from "./modules/profileStats.js";


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
            const body = {
                'old_password' : document.getElementById("username-password").value,
                'new_username' : document.getElementById("new-username").value
            };
            
            try {
                const response = await fetchJson("/api/users/change_username", 'POST', body);
                if (response.status === 200) {
                    alert("Username changed, please re-login with your new credentials");
                    await fetch("/api/users/logout");
                    window.location.href = "/login";
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
                'old_password' : document.getElementById("deleteU-password").value
            };

            try {
                /*
                const response = await fetchJson("/api/users/delete_account", 'DELETE', body);
                if (response.status === 200) {
                    alert("Account has been deleted");
                    await fetch("/api/users/logout");
                    window.location.href = "/";
                } 
                this.feedbackMsg = await response.text()*/
                this.feedbackMsg = "Not implemented"
            } catch (e) {
                console.log(e);
            }
        }
    }

});
