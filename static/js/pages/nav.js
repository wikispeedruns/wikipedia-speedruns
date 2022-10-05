
import Vue from 'vue/dist/vue.esm.js';



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
        async accountPage(event)
        {
            window.location.href = "/account"
        }
    }

});
