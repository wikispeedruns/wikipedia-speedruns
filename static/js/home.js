async function getPrompts()
{
    const response = await fetch("/api/sprints/active");
    const prompts = await response.json();

    return prompts;
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
    },

    created: async function() {
        this.topUsers = await getTopUsers();

        const prompts = await getPrompts();
        this.dailyPrompts = prompts.filter(p => p.rated)
        this.activePrompts = prompts.filter(p => !p.rated)
    }
})
