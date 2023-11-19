
import Vue from 'vue/dist/vue.esm.js';

// getTheme retrieves theme from localStorage
// returns string of either "dark" or "light"
function getTheme() {
    let currentTheme = localStorage.getItem("user-theme");
    if (currentTheme == "dark") {
        return "dark";
    } else {
        return "light";
    }
}

async function setTheme(theme) {
    var htmlElement = document.querySelector('html');

    // set bootstrap theme to root html div
    // https://getbootstrap.com/docs/5.3/customize/color-modes/
    htmlElement.setAttribute('data-bs-theme', theme);

    setWikiTheme(theme);
}

// theme:string is either 'dark' or 'light'
async function setWikiTheme(theme) {
    if (theme == "dark") {
        var toc = document.querySelector('#toc');
        if (toc != null) {
            toc.classList.add("wiki-dark");
        }

        const allTables = document.querySelector('table');
        if (allTables != null) {
            allTables.classList.add("wiki-dark");
        }
    } else {
        var toc = document.querySelector('#toc');
        if (toc != null) {
            toc.classList.remove("wiki-dark");
        }

        const allTables = document.querySelector('table');
        if (allTables != null) {
            allTables.classList.remove("wiki-dark");
        }
    }
}

function saveTheme(theme) {

}

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
        },
        async switchTheme() {
            let currentTheme = getTheme();

            
        }
    }

});
