
import Vue from 'vue/dist/vue.esm.js';

// getTheme retrieves theme from localStorage
//      allowing settings to persist to other pages and from refreshes.
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
        // var wikiInsert = document.querySelector('#wikipedia-frame');
        // wikiInsert.classList.add('wiki-dark');



        // var toc = document.querySelector('#toc');
        // if (toc != null) {
        //     toc.classList.add("wiki-dark");
        // }

        // const allTables = document.querySelector('table');
        // if (allTables != null) {
        //     allTables.classList.add("wiki-dark");
        // }
    } else {
        // var wikiInsert = document.querySelector('#wikipedia-frame');
        // wikiInsert.classList.remove('wiki-dark');



        // var toc = document.querySelector('#toc');
        // if (toc != null) {
        //     toc.classList.remove("wiki-dark");
        // }

        // const allTables = document.querySelector('table');
        // if (allTables != null) {
        //     allTables.classList.remove("wiki-dark");
        // }
    }
}

function saveTheme(theme) {
    localStorage.setItem("user-theme", theme);
}

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#nav',

    data: function() {
        return {
            username: "",
            loggedIn: false,
            /* Set theme to be reactive so findable by v-if/else */
            theme: "",
        }
    },

    created: function() {
        if ("username" in serverData) {
            this.loggedIn = true;
            this.username = serverData["username"];
            this.isAdmin = serverData["admin"];
        }

        const theme = getTheme();
        setTheme(theme);
        this.theme = theme;
    },

    methods: {
        async accountPage(event)
        {
            window.location.href = "/account"
        },
        switchTheme() {
            let currentTheme = getTheme();
            let newTheme = "";
            if (currentTheme != "dark") {
                newTheme = "dark";
            } else {
                newTheme = "light";
            }
            setTheme(newTheme);
            saveTheme(newTheme);

            this.theme = newTheme;
        },
        getTheme:() => {
            let currentTheme = localStorage.getItem("user-theme");
            console.log(currentTheme);
            if (currentTheme == "dark") {
                return "dark";
            } else {
                return "light";
            }
        }
        
    }

});
