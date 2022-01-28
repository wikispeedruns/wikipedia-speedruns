import { serverData } from "./modules/serverData.js";

const profile_name = serverData["profile_name"];

function update_data(runs, user) {
            
    try {
        vm.totalratedruns.val = runs['total_prompts'];
        vm.emailverified.val = user['email_confirmed'] ? "Yes" : "No";
        
        vm.user_name.val = user['username'];
    } catch (error) {
        console.error(error);
        window.location.href = "/error";
    }
}

async function get_data(usern) {
    
    response = await fetch("/api/profiles/" + usern + "/totals");
    const runs = await response.json(); 

    //console.log(runs);

    response = await fetch("/api/profiles/" + usern);
    const user = await response.json(); 

    //console.log(user);

    update_data(runs, user);
    
}

let vm = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        user_name: {
            field: "Username",
            val: "test1"
        },
        skillrating: {
            field: "Skill Rating",
            val: "test2"
        },
        totalratedruns: {
            field: "Total runs",
            val: "test3"
        },
        emailverified: {
            field: "Email Verification Status",
            val: "test4"
        },
        profileage: {
            field: "Profile Age",
            val: "test5"
        },
    },

    created: async function () {
        get_data(profile_name);
    }
});



