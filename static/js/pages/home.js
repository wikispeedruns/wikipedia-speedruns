import Vue from 'vue/dist/vue.esm.js';

import { MarathonPrompts } from "../modules/game/marathon/marathonPrompts.js";
import { CustomPlay } from "../modules/customPlay.js";

import { uploadLocalSprints, getLocalSprints } from "../modules/localStorage/localStorageSprint.js";
import { uploadLocalMarathons, getLocalMarathons } from "../modules/localStorage/localStorageMarathon.js";
import { uploadLocalQuickRuns } from "../modules/localStorage/localStorageQuickRun.js";
import { generateStreakText } from "../modules/streaks.js";
import { getUserLobby } from "../modules/lobby/utils.js";

async function getPrompts()
{
    const response = await fetch("/api/sprints/active");
    const prompts = await response.json();

    return prompts;
}

async function getBackupPrompts()
{
    const response = await fetch("/api/sprints/archive?limit=10");
    const resp = await response.json();

    return resp["prompts"].filter(p => !p["active"]);
}

async function getMarathonPrompts()
{
    const response = await fetch("/api/marathon/all");
    return await response.json();
}

async function getStreak() {
    const response = await fetch("/api/profiles/streak");
    return await response.json();
}


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'marathon-prompts': MarathonPrompts,
        'custom-play': CustomPlay
    },
    data: {
        dailyPrompts: [],
        activePrompts: [],
        topUsers: [],
        marathonPrompts: [],
        timeLeft: "",
        username: serverData["username"],
        loggedIn: null,

        streakText: '',

        lobbies: [],

        isMobile: false,
    },
    methods: {
        alertLogin: (e) => {
            e.preventDefault();
            alert("Please login if you would like to play the prompt of the day!");
        },

        copyInvite: function (lobby) {
            const link = `Join my Wikispeedruns lobby\n${window.location.origin}/lobby/${lobby.lobby_id}\nPasscode: ${lobby.passcode}`
            navigator.clipboard.writeText(link);
            document.getElementById("custom-tooltip-"+lobby.lobby_id).innerHTML = "Invite copied!";
            setTimeout(function() {
                document.getElementById("custom-tooltip-"+lobby.lobby_id).innerHTML = "- Copy invite -";
            }, 1500);
        },

        getDate: function (string) {
            let date = new Date(string);
            return date.toLocaleDateString();
        },
    },

    created: async function() {
        this.isMobile = window.screen.width < 768;
        this.loggedIn = "username" in serverData;

        if (this.loggedIn) {
            await uploadLocalSprints();
            await uploadLocalMarathons();
            await uploadLocalQuickRuns();
        }

        //this.topUsers = await getTopUsers();
        this.marathonPrompts = await getMarathonPrompts();

        const prompts = await getPrompts();
        this.dailyPrompts = prompts.filter(p => p.rated);
        this.activePrompts = prompts.filter(p => !p.rated);

        this.lobbies = await getUserLobby(this.loggedIn);

        if (this.activePrompts.length === 0) {
            this.activePrompts = await getBackupPrompts();
        }

        if (this.dailyPrompts.length > 0) {
            // Add Z to indicate UTC format
            const endTime = new Date(this.dailyPrompts[0]["active_end"] + "Z");

            const timerInterval = setInterval(() => {
                const now = new Date();

                let diff = (endTime - now) / 1000;

                const s = Math.round(diff % 60).toString().padStart(2, "0");
                diff /= 60;
                diff = Math.floor(diff);

                const m = Math.round(diff % 60).toString().padStart(2, "0");
                diff /= 60;

                const h = Math.floor(diff).toString().padStart(2, "0");

                this.timeLeft = `${h}:${m}:${s}`;
            }, 1000);

        }

        if (!this.loggedIn) {

            const localSprints = getLocalSprints();

            //console.log("Locally stored sprints: ")
            //console.log(localSprints)

            for (let prompt of this.dailyPrompts){
                for (let run_id of Object.keys(localSprints)) {
                    if (parseInt(localSprints[run_id].prompt_id) === prompt.prompt_id) {
                        prompt.played = true
                    }
                }
            }

            for (let prompt of this.activePrompts){
                for (let run_id of Object.keys(localSprints)) {
                    if (parseInt(localSprints[run_id].prompt_id) === prompt.prompt_id) {
                        prompt.played = true
                    }
                }
            }

        } else {
            const resp = await getStreak();
            this.streakText = generateStreakText(resp);
        }
    }
})
