const USERS_COLOR = "#347aeb";
const USERS_SUBCOLOR = "#f2a257";
const SPRINTS_COLOR = "#9E58EE";
const SPRINTS_SUBCOLOR = "#ffdb99";
const MARATHON_COLOR = "#EB8258";
const MARATHON_SUBCOLOR = "#58ebbf";

function update_totals(totals) {
    app.totals.users = totals['users_total'];
    app.totals.google_users = totals['goog_total'];
    
    app.totals.runs = totals['sprints_total'];
    app.totals.marathon_runs = totals['marathons_total'];
    app.totals.finished_runs = totals['sprints_finished'];
    app.totals.finished_marathons = totals['marathons_finished'];
   
    let user_runs = totals['user_runs'];
    let user_finished_runs = totals['user_finished_runs'];
    let user_marathons = totals['user_marathons'];
    let user_finished_marathons = totals['user_finished_marathons'];

    app.totals.pct_goog_users = ((app.totals.google_users / app.totals.users) * 100).toFixed(2);
    app.totals.pct_user_runs = ((user_runs / app.totals.runs) * 100).toFixed(2);
    app.totals.pct_user_finished_runs = ((user_finished_runs / app.totals.finished_runs) * 100).toFixed(2);
    app.totals.pct_user_marathons = ((user_marathons / app.totals.marathon_runs) * 100).toFixed(2);
    app.totals.pct_user_finished_marathons = ((user_finished_marathons / app.totals.finished_marathons) * 100).toFixed(2);
}

function update_daily(daily_totals) {
    app.daily.users = daily_totals['daily_new_users'];
     // remove the first day, an outlier
    app.daily.users.shift();

    app.daily.sprint_runs = daily_totals['daily_sprints'];
    app.daily.finished_sprint_runs = daily_totals['daily_finished_sprints'];

    app.daily.sprint_runs_per_user = daily_totals['avg_user_plays'];
    app.daily.finished_sprint_runs_per_user = daily_totals['avg_user_finished_plays'];
    app.daily.active_users = daily_totals['active_users'];
}

async function get_data() {
    let response = await fetch("/api/stats/totals");
    const totals = await response.json(); 
    update_totals(totals);

    response = await fetch("/api/stats/daily");
    const daily_totals = await response.json();
    update_daily(daily_totals);

    calculate_weekly_change();
}

function calculate_weekly_change() {
    let last_week_users = app.daily.users[app.daily.users.length - 7]['total'];
    app.weekly.user_change = app.totals.users - last_week_users;

    let last_week_runs = app.daily.sprint_runs[app.daily.sprint_runs.length - 7]['total'];
    app.weekly.runs_change = app.totals.runs - last_week_runs;

    let last_week_finished_runs = app.daily.finished_sprint_runs[app.daily.finished_sprint_runs.length - 7]['total'];
    app.weekly.finished_runs_change = app.totals.finished_runs - last_week_finished_runs;
}

async function draw_graphs() {
    new Chart("daily-users", {
        type: 'line',
        data: {
          labels: app.daily.users.map(({day}) => day),
          datasets: [{ 
              data: app.daily.users.map(({total}) => total),
              label: "Total Users",
              borderColor: USERS_COLOR, 
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
              borderColor: USERS_COLOR,
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
          labels: app.daily.sprint_runs.map(({day}) => day),
          datasets: [{ 
              data: app.daily.sprint_runs.map(({total}) => total),
              label: "Total Sprint Runs",
              borderColor: SPRINTS_COLOR,
              fill: false
            },
            { 
                data: app.daily.finished_sprint_runs.map(({total}) => total),
                label: "Total Finished Sprint Runs",
                borderColor: SPRINTS_SUBCOLOR,
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

    new Chart("daily-new-runs", {
        type: 'line',
        data: {
          labels: app.daily.sprint_runs.map(({day}) => day),
          datasets: [{ 
              data: app.daily.sprint_runs.map(({daily_plays}) => daily_plays),
              label: "New Sprint Runs",
              borderColor: SPRINTS_COLOR,
              fill: false
            },
            { 
                data: app.daily.finished_sprint_runs.map(({daily_plays}) => daily_plays),
                label: "New Finished Sprint Runs",
                borderColor: SPRINTS_SUBCOLOR,
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
            plugins: {
                subtitle: {
                    display: true,
                    text: 'Note: We stopped submitting start time data for unfinished runs on 2/20',
                    color: 'red',
                    font: {
                        weight: 'bold',
                      },
                }
            }
        }
    });

    new Chart("daily-active-users", {
        type: 'line',
        data: {
          labels: app.daily.active_users.map(({day}) => day),
          datasets: [{ 
              data: app.daily.active_users.map(({active_users}) => active_users),
              label: "Users That Finished A Sprint Run",
              borderColor: USERS_COLOR,
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
          labels: app.daily.sprint_runs_per_user.map(({day}) => day),
          datasets: [{ 
              data: app.daily.sprint_runs_per_user.map(({sprint_runs_per_user}) => sprint_runs_per_user),
              label: "Average User Sprint Runs",
              borderColor: SPRINTS_COLOR,
              fill: false
            },
            { 
                data: app.daily.finished_sprint_runs_per_user.map(({finished_sprint_runs_per_user}) => finished_sprint_runs_per_user),
                label: "Average Finished User Sprint Runs",
                borderColor: SPRINTS_SUBCOLOR,
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
            google_users: 0,
            runs: 0,
            marathons_runs: 0,
            finished_runs: 0,
            finished_marathons: 0,
            pct_goog_users: 0.0,
            pct_user_runs: 0.0,
            pct_user_finished_runs: 0.0,
            pct_user_marathons: 0.0,
            pct_user_finished_marathons: 0.0,
        },
        weekly: {
            user_change: 0.0,
            runs_change: 0.0,
            finished_runs_change: 0.0,
        },
        daily: {
            users: [],
            sprint_runs: [],
            finished_sprint_runs: [],
            sprint_runs_per_user: [],
            finished_sprint_runs_per_user: [],
            active_users: []
        },
    },

    created: async function () {
        await get_data();
        draw_graphs();
    }
});