var vm; 

function update_data(runs, user) {
            
    try {
        vm.totalratedruns = runs['total_prompts'];
        if (user['email_confirmed']) {
            vm.emailverified = "Yes";
        } else {
            vm.emailverified = "No";
        }
        
        vm.user_name = user['username'];
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

window.addEventListener("load", function() {

    get_data(profile_name);

    vm = new Vue({
        el: '#app',
        data: {
            user_name: '',
            skillrating:'',
            totalratedruns:'',
            emailverified:'',
            profileage:''
        }
    });
});
