import { serverData } from "./modules/serverData.js";
import { fetchJson } from "./modules/fetch.js";


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    
    data: {
        username: "",
        loggedIn: false,
        emailConfirmed: false,
        feedbackMsg: '',
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
        }
    }

});
