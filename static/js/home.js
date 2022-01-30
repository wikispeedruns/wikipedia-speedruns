async function getPromptsPublic()
{
    const response = await fetch("/api/prompts/public");
    const prompts = await response.json();

    return prompts;
}

async function getDailyPrompts()
{
    const response = await fetch("/api/prompts/daily");
    return await response.json();
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
        publicPrompts: [],
        dailyPrompts: [],
        topUsers: [],
        marathonPrompts: [],
    },

    created: async function() {
        this.topUsers = await getTopUsers();
        this.publicPrompts = await getPromptsPublic(); 
        this.dailyPrompts = await getDailyPrompts();
        this.marathonPrompts = await getMarathonPrompts(); 
    }
})
