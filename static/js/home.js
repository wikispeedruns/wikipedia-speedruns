import { serverData } from "./modules/serverData.js";

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

async function getTopUsers()
{
    const response = await fetch("/api/ratings");
    const ratings = await response.json();

    return ratings;
}


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        dailyPrompts: [],
        activePrompts: [],
        topUsers: [],
        timeLeft: "",
        loggedIn: false,
    },
    methods: {
        alertLogin: () => {
            alert("Please login if you would like to play the prompt of the day!");
        }
    },

    created: async function() {
        if ("username" in serverData) {
            this.loggedIn = true;
        }

        this.topUsers = await getTopUsers();

        const prompts = await getPrompts();
        this.dailyPrompts = prompts.filter(p => p.rated);
        this.activePrompts = prompts.filter(p => !p.rated);


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

    }
})
