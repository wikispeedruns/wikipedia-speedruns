import { serverData } from "./modules/serverData.js";


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#nav',
    
    data: {
        username: "",
        loggedIn: false,
    },

    created: function() {
        if ("username" in serverData) {
            this.loggedIn = true;
            this.username = serverData["username"];
            this.isAdmin = serverData["admin"];
        }
    },

    methods: {
        async handleLogout(event)
        {
            event.preventDefault();
            await fetch("/api/users/logout", {method : "POST"});
            window.location.href = "/";
        }
    }

});
