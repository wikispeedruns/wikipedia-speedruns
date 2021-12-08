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
            
    vm.totalratedruns = runs.length;
    vm.email = user[0]['email'];
    if (user[0]['email_confirmed']) {
        vm.emailverified = "Yes";
    } else {
        vm.emailverified = "No";
    }
    
    vm.user_name = user[0]['username'];
}

async function get_data(usern) {
    response = await fetch("/api/runs/user/" + usern);
    const runs = await response.json(); 

    //console.log(runs);

    response = await fetch("/api/users/get_user_data/" + usern);
    const user = await response.json(); 

    //console.log(user);

    update_data(runs, user);
}



async function get_achievement_data(usern) {
    response = await fetch("/api/achievements/user/" + usern);
    const user_ach = await response.json(); 

    response = await fetch("/api/achievements/get_achievements");
    const all_ach = await response.json(); 

    
    console.log(user_ach);
    console.log("==================");
    console.log(all_ach);
    console.log("==================");

    achievementsTable = document.getElementById("achievements")
    
    for (i = 0; i < all_ach['achievements'].length; i++) {
        
        var row = document.createElement("tr");
        
        var picSlot = document.createElement("td");
        var pic = document.createElement("img");
        
        if (user_ach[all_ach['achievements'][i]['name']] == false) {
            pic.src = "/static/assets/achievementIcons/locked.png";
        } else {
            pic.src = all_ach['achievements'][i]['imgURL'];
        }
        pic.width = '100';
        
        picSlot.appendChild(pic);

        var textSlot = document.createElement("td");
        var title = document.createElement("p");
        title.innerHTML = all_ach['achievements'][i]['name'];
        title.style.fontWeight = 'bold';
        var desc = document.createElement("p");
        desc.innerHTML = all_ach['achievements'][i]['description'];

        textSlot.appendChild(title);
        if (all_ach['achievements'][i]['secret'] == false) {
            textSlot.appendChild(desc);
        }

        var statusSlot = document.createElement("td");
        var status = document.createElement("p");
        if (user_ach[all_ach['achievements'][i]['name']] == false) {
            status.innerHTML = "Incomplete...";
        } else {
            status.innerHTML = "Complete!";
        }
        statusSlot.appendChild(status)


        row.appendChild(picSlot);
        row.appendChild(textSlot);
        row.appendChild(statusSlot);

        achievementsTable.appendChild(row);
    }

}