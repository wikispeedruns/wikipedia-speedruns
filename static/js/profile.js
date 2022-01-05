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
            
    vm.totalratedruns = runs['total_prompts'];
    vm.email = user['email'];
    if (user['email_confirmed']) {
        vm.emailverified = "Yes";
    } else {
        vm.emailverified = "No";
    }
    
    vm.user_name = user['username'];
}

async function get_data(usern) {
    
    response = await fetch("/api/profiles/" + usern + "/totals");
    const runs = await response.json(); 

    console.log(runs);

    response = await fetch("/api/profiles/" + usern);
    const user = await response.json(); 

    console.log(user);

    update_data(runs, user);
}

