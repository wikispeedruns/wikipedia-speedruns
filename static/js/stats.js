function update_totals(totals) {
    app.totals.users = totals['users_total'];
    app.totals.runs = totals['sprints_total'];
    app.totals.finished_runs = totals['sprints_finished'];
}

function update_daily(d_totals) {
    app.daily.users = d_totals['daily_new_users'];
    app.daily.runs = d_totals['daily_plays'];
    app.daily.finished_runs = d_totals['daily_finished_plays'];
    app.daily.plays_per_user = d_totals['avg_user_plays'];
    app.daily.active_users = d_totals['active_users'];
}

async function get_data() {
    let response = await fetch("/api/stats/totals");
    const totals = await response.json(); 
    update_totals(totals);

    response = await fetch("/api/stats/daily");
    const d_totals = await response.json();
    update_daily(d_totals);
}

async function draw_graphs() {
    new Chart("daily-users", {
        type: 'line',
        data: {
          labels: app.daily.users.map(({day}) => day),
          datasets: [{ 
              data: app.daily.users.map(({total}) => total),
              label: "Total Users",
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

    new Chart("daily-new-users", {
        type: 'line',
        data: {
          labels: app.daily.users.map(({day}) => day),
          datasets: [{ 
              data: app.daily.users.map(({daily_users}) => daily_users),
              label: "New Users",
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

    new Chart("daily-runs", {
        type: 'line',
        data: {
          labels: app.daily.runs.map(({day}) => day),
          datasets: [{ 
              data: app.daily.runs.map(({daily_plays}) => daily_plays),
              label: "Daily Plays",
              borderColor: "#3e95cd",
              fill: false
            }
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


    new Chart("daily-finished-runs", {
        type: 'line',
        data: {
          labels: app.daily.finished_runs.map(({day}) => day),
          datasets: [{ 
              data: app.daily.finished_runs.map(({daily_plays}) => daily_plays),
              label: "Daily Finished Plays",
              borderColor: "#3e95cd",
              fill: false
            }
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

    new Chart("daily-active-users", {
        type: 'line',
        data: {
          labels: app.daily.active_users.map(({day}) => day),
          datasets: [{ 
              data: app.daily.active_users.map(({active_users}) => active_users),
              label: "Daily Active Users",
              borderColor: "#3e95cd",
              fill: false
            }
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

    new Chart("daily-average-user-plays", {
        type: 'line',
        data: {
          labels: app.daily.plays_per_user.map(({day}) => day),
          datasets: [{ 
              data: app.daily.plays_per_user.map(({plays_per_user}) => plays_per_user),
              label: "Average User Plays",
              borderColor: "#3e95cd",
              fill: false
            }
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
        daily: {
            users: [],
            runs: [],
            finished_runs: [],
            plays_per_user: [],
            active_users: []
        },
    },

    created: async function () {
        await get_data();
        draw_graphs();
    }
});