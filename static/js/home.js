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

async function getMarathonPrompts()
{
    const response = await fetch("/api/marathon/all");
    return await response.json();
}


var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        dailyPrompts: [],
        activePrompts: [],
        topUsers: [],
        marathonPrompts: [],
        timeLeft: "",
    },

    created: async function() {
        this.topUsers = await getTopUsers();
        this.marathonPrompts = await getMarathonPrompts(); 

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
