import Vue from "vue/dist/vue.esm.js";

import { fetchJson } from "../../modules/fetch.js";
import { checkArticles, getSupportedLanguages, getRandomArticle } from "../../modules/wikipediaAPI/util.js";
import { PromptGenerator } from "../../modules/generator.js"
import { AutocompleteInput } from "../../modules/autocomplete.js"
import { UserDisplay } from "../../modules/userDisplay.js"

const LOBBY_ID = serverData["lobby_id"];
const successMessage = "Added prompt to lobby!";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'prompt-generator': PromptGenerator,
        'ac-input': AutocompleteInput,
        'user': UserDisplay
    },
    data: {
        startPrompt:"",
        endPrompt:"",
        language: "en",
        languages: [],
        addPromptMessage:"",

        prompts: [],

        link: "",

        lobbyInfo: {
            "name": null,
            "desc": null,
            "user": {
                "name": null,
                "owner": null
            }
        },

        editPrompts: false,
        selectedPrompts: [],

        users: null,
        anon_users: null,

        messageType: null,
        messageTimer: null
    },


    created: async function() {
        this.getPrompts();
        this.getLobbyInfo();
    },

    mounted: function() {
        this.link = window.location.href;
        this.getLanguages();
    },

    methods: {

        copyInviteLink() {
            const link = `Join my Wikispeedruns lobby\n${window.location.href}\nPasscode: ${this.lobbyInfo.passcode}`
            document.getElementById("custom-tooltip").style.display = "inline";
            navigator.clipboard.writeText(link);
            setTimeout(function() {
                document.getElementById("custom-tooltip").style.display = "none";
            }, 1500);
        },

        selectPrompt(prompt_id) {
            if (this.selectedPrompts.has(prompt_id)) {
                this.selectedPrompts.delete(prompt_id);
            } else {
                this.selectedPrompts.add(prompt_id);
            }
        },

        selectAllPrompts() {
            this.clearSelectedPrompts();
            for (const prompt of this.prompts) {
                this.selectedPrompts.push(prompt.prompt_id);
            }
        },

        clearSelectedPrompts() {
            this.selectedPrompts = [];
        },

        async getLobbyInfo() {
            const resp = await fetchJson(`/api/lobbys/${LOBBY_ID}`);
            this.lobbyInfo = await resp.json();

            if (this.lobbyInfo.user.owner) {
                await this.getLobbyUsers();
            }
        },

        async getPrompts() {
            const resp = await fetchJson(`/api/lobbys/${LOBBY_ID}/prompts`);
            this.prompts = await resp.json();

        },

        async getLanguages() {
            this.languages = await getSupportedLanguages();
        },

        async generateRndPrompt(prompt) {
            if (this.language === 'en') {
                [this[prompt]] = await this.$refs.pg.generatePrompt();
            } else {
                this[prompt] = await getRandomArticle(this.language);
            }
        },

        clearMessage() {
            this.messageType = null;
        },

        setMessage(messageType) {
            this.messageType = messageType;
            clearTimeout(this.messageTimer);
            this.messageTimer = setTimeout(this.clearMessage, 5000);
        },

        async considerPrompt() {
            this.addPromptMessage = "";

            const res = await checkArticles(this.startPrompt, this.endPrompt, this.language);
            if(res.err) {
                this.addPromptMessage = res.err;
                return;
            }

            console.log(res);

            const resp = await fetchJson(`/api/lobbys/${LOBBY_ID}/prompts`, "POST", {
                "start": res.body.start,
                "end": res.body.end,
                "language": res.body.lang,
            });
            if(resp.status !== 200){
                this.addPromptMessage = "Error adding prompt to database"
                return;
            }

            this.addPromptMessage = successMessage;
        },

        async addPrompt() {
            await this.considerPrompt();

            const messageType = this.addPromptMessage == successMessage ? 'success' : 'danger';
            this.setMessage(messageType);

            this.getPrompts();
        },

        async deletePrompts() {
            if (!confirm("Are you sure you want to delete the selected prompts and their runs?")) {
               return;
            }
            if(this.selectedPrompts.length == 0){
                console.log("No prompts selected");
                return;
            }

            const resp = await fetchJson(`/api/lobbys/${LOBBY_ID}/prompts`, "DELETE", {
                "prompts": this.selectedPrompts,
            });

            this.editPrompts = false;
            this.clearSelectedPrompts();
            this.getPrompts();
        },


        async getLobbyUsers() {

            Promise.all([
                fetchJson(`/api/lobbys/players/${LOBBY_ID}`, "GET"),
                fetchJson(`/api/lobbys/anon_players/${LOBBY_ID}`, "GET")
            ])
            .then(responses =>
                Promise.all(responses.map(res => res.json()))
            ).then(resp => {
                this.users = resp[0];
                this.anon_users = resp[1];
            }).catch(err => console.log(err));

        },

        async makeHost(user_id, username) {
            if (!confirm(`Are you sure you want to make ${username} the lobby host?`)) {
                return;
            }

            try {
                const resp = await fetchJson(`/api/lobbys/change_host/${LOBBY_ID}`, "PATCH", {
                    "target_user_id": user_id,
                });

                alert(`${username} is now host!`);
                window.location.reload();
            } catch (e) {
                console.log(e)
                alert(e);
            }
        },

        toggleDropdown(id) {
            document.getElementById(id).classList.toggle("active-dropdown")
        }
    }


})
