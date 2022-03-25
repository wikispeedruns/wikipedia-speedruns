function update_data(totals) {
        console.log(totals);
        app.totals.users = totals['users_total'];
        app.totals.runs = totals['sprints_total'];
        app.totals.finished_runs = totals['sprints_finished'];
}

async function get_data() {
    let response = await fetch("/api/stats/totals");
    const totals = await response.json(); 

    update_data(totals);
    response = await fetch("/api/stats/weekly");
    const w_totals = await response.json();

    app.weekly.users = w_totals['users_weekly'];
    app.weekly.runs = w_totals['plays_weekly'];
    app.weekly.finished_runs = w_totals['finished_plays_weekly'];

    response = await fetch("/api/stats/daily");
    const d_totals = await response.json();

    app.daily.avg_unique_plays = d_totals['avg_unique_user_plays'];

}

async function draw_graphs() {
    new Chart("line-chart", {
        type: 'line',
        data: {
          labels: app.weekly.users.map(({week}) => week),
          datasets: [{ 
              data: app.weekly.users.map(({weekly_users}) => weekly_users),
              label: "Weekly New Users",
              borderColor: "#3e95cd",
              fill: false
            },
          ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
        }
    });   
}

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        totals: {
            users: 0,
            runs: 0,
            finished_runs: 0,
        },
        weekly: {
            users: [],
            runs: [],
            finished_runs: [],
        },
        daily: {
            avg_unique_plays: [],
        },
    },

    created: async function () {
        await get_data();
        draw_graphs();
    }
});