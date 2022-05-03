import { serverData } from "./modules/serverData.js";


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    
    data: {
        username: "",
        loggedIn: false,
        emailConfirmed: false,
    },

    created: async function() {
        if ("username" in serverData) {
            this.loggedIn = true;
            this.username = serverData["username"];
            this.isAdmin = serverData["admin"];
        } else {
            window.location.href = "/";  // redirect home if not logged in
        }

        this.getEmailConfirmed()
        // const response = await fetch("/api/users/check_email_confirmation", {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify(serverData["username"])
        // });

        // this.emailConfirmed = await response.text();
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
        }
    }

});
