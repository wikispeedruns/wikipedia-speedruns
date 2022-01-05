async function getPromptsHome()
{
    queryString = "";

    // Defined in base.html based on template
    if (!user_id) {
        queryString = "?public=true"
    }

    const response = await fetch("/api/prompts" + queryString);
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
        this.prompts = await getPromptsHome();    
    }
})
