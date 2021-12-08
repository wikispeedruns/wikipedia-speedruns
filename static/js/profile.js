var vm = new Vue({
    el: '#app',
    data: {
        user_name: 'test',
        skillrating:'--',
        totalratedruns:'20',
        email:'test@123.org',
        emailverified:'True',
        profileage:'--',
        articleCount:0
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

    let temp = get_most_visited_pages(runs)
    vm.articleCount = temp[1]
    convMostVisitedToHTML(temp[0]);
}

function convMostVisitedToHTML(pages) {
    var el = document.getElementById("mostvisitedpages");
    for (var i = 0 ; i < pages.length; i++) {
        var row = document.createElement("tr");
        var name = document.createElement("td");
        name.innerHTML = pages[i]['name'];
        var times = document.createElement("td");
        times.innerHTML = pages[i]['times'];
        times.style.paddingLeft = "25px";
        row.appendChild(name)
        row.appendChild(times)
        el.appendChild(row)
    }
}

function get_most_visited_pages(runs) {

    arr = []
    count = {}
    for (var i = 0; i < runs.length; i++) {
        //console.log(runs[i]['path'])
        for (var j = 0; j < runs[i]['path'].length; j++) {
            if (count[runs[i]['path'][j]] == null) {
                count[runs[i]['path'][j]] = 1;
            } else {
                count[runs[i]['path'][j]] ++;
            }
        }
    }

    //console.log(count)

    var keys = Object.keys(count)
    var l = keys

    keys.sort((b, a) => {
        if (count[a] > count[b]) {
            return 1
        } else if (count[b] > count[a]) {
            return -1
        }
        return 0
    })

    if (keys.length > 4) {
        l = keys.slice(0, 5)
    }

    l.forEach(element => {
        arr.push({"name":element, "times":count[element]})
    })

    return [arr, keys.length]
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

    
    //console.log(user_ach);
    //console.log("==================");
    //console.log(all_ach);
    //console.log("==================");

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