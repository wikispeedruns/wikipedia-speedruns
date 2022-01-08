async function getPromptsPublic()
{
    const response = await fetch("/api/prompts/public");
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
        prompts: [],
        topUsers: []
    },

    created: async function() {
        this.topUsers = await getTopUsers();
        this.prompts = await getPromptsPublic(); 
    }
})
