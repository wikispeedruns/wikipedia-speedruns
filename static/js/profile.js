var vm = new Vue({
    el: '#app',
    data: {
        user_name: 'test',
        skillrating:'1000',
        totalratedruns:'20',
        email:'test@123.org',
        emailverified:'True',
        profileage:'32 Days'
    }
});


/*
Vue.component('info-item', {
    props: ['info'],
    template: '<tr><td>Hello{{info.field_name}}</td><td>{{info.value}}</td></tr>'
});

var vm = new Vue({
    el: '#app',
    data: {
        fields: [
            {field_name: "Username", value: ""},
            {field_name: "Email", value: ""},
            {field_name: "Profile Age", value: ""},
            {field_name: "Skill Rating", value: ""},
            {field_name: "Total Rated Runs", value: ""},
            {field_name: "Email Verification Status", value: ""},
        ]
    }
});
*/

function update_data(runs, user) {
            
    console.log(runs.length);
    console.log(user[0]['user_id']);
    console.log(user[0]['email']);
    console.log(user[0]['email_confirmed']);
    console.log(user[0]['username']);
}

async function get_data(usern) {
    response = await fetch("/api/runs/user/" + usern);
    const runs = await response.json(); 

    console.log(runs);

    response = await fetch("/api/users/get_user_data/" + usern);
    const user = await response.json(); 

    console.log(user);

    update_data(runs, user);
}

