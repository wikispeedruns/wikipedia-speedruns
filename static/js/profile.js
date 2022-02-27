import { serverData } from "./modules/serverData.js";

const profile_name = serverData["profile_name"];

function update_data(runs, user) {
    try {
        vm.totalratedruns.val = runs['total_prompts'];
        vm.emailverified.val = user['email_confirmed'] ? "Yes" : "No";
        vm.user_name.val = user['username'];
        vm.skillrating.val = user['rating'];

        let date = new Date(user['join_date']);
        vm.profileage.val = date.toLocaleDateString();
    } catch (error) {
        console.error(error);
        window.location.href = "/error";
    }
}

async function get_data(username) {
    let response = await fetch("/api/profiles/" + username + "/stats");
    const runs = await response.json(); 

    response = await fetch("/api/profiles/" + username);
    const user = await response.json(); 

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
            field: "Total Runs",
            val: "test3"
        },
        emailverified: {
            field: "Email Verified",
            val: "test4"
        },
        profileage: {
            field: "Member Since",
            val: "test5"
        },
    },

    created: async function () {
        get_data(profile_name);
    }
});



