import Vue from "vue/dist/vue.esm.js";
import { fetchJson } from "../../modules/fetch.js";

const Chart = require('chart.js');


const USERS_COLOR = "#347aeb";
const USERS_SUBCOLOR = "#f2a257";
const SPRINTS_COLOR = "#9E58EE";
const SPRINTS_SUBCOLOR = "#ffdb99";
const MARATHON_COLOR = "#EB8258";
const MARATHON_SUBCOLOR = "#58ebbf";
const LOBBIES_COLOR = "#e13e2e";
const LOBBIES_SUBCOLOR = "#D7AD38";

function update_totals(totals) {
    app.totals.users = totals['users_total'];
    app.totals.google_users = totals['goog_total'];

    app.totals.runs = totals['sprints_total'];
    app.totals.marathon_runs = totals['marathons_total'];
    app.totals.finished_runs = totals['sprints_finished'];
    app.totals.finished_marathons = totals['marathons_finished'];
    app.totals.lobby_runs = totals['lobby_runs_total'];
    app.totals.finished_lobby_runs = totals['lobby_runs_finished'];
    app.totals.created_lobbies = totals['lobbies_created'];

    app.totals.daily_active_users = totals['daily_active_users'];
    app.totals.weekly_active_users = totals['weekly_active_users'];
    app.totals.monthly_active_users = totals['monthly_active_users'];
    app.totals.daily_active_users_finished = totals['daily_active_users_finished'];
    app.totals.weekly_active_users_finished = totals['weekly_active_users_finished'];
    app.totals.monthly_active_users_finished = totals['monthly_active_users_finished'];

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

    app.daily.lobby_runs = daily_totals['daily_lobby_runs'];
    app.daily.finished_lobby_runs = daily_totals['daily_finished_lobby_runs'];
    app.daily.created_lobbies = daily_totals['daily_created_lobbies'];

    app.daily.lobby_runs_per_user = daily_totals['avg_user_lobby_plays'];
    app.daily.finished_lobby_runs_per_user = daily_totals['avg_user_finished_lobby_plays'];
    app.daily.active_lobby_users = daily_totals['active_lobby_users'];
}

async function get_data(res=null) {
    let response = res ?? await fetch("/api/stats/all");
    let res_json = await response.json();
    const all_stats = JSON.parse(res_json['stats_json'])['stats'];

    update_totals(all_stats);
    update_daily(all_stats);

    app.last_updated = new Date(res_json['timestamp']);
    calculate_weekly_change();
}

function calculate_weekly_change() {
    let last_week_users = app.daily.users[app.daily.users.length - 7]['total'];
    app.weekly.user_change = app.totals.users - last_week_users;

    let last_week_runs = app.daily.sprint_runs[app.daily.sprint_runs.length - 7]['total'];
    app.weekly.runs_change = app.totals.runs - last_week_runs;

    let last_week_finished_runs = app.daily.finished_sprint_runs[app.daily.finished_sprint_runs.length - 7]['total'];
    app.weekly.finished_runs_change = app.totals.finished_runs - last_week_finished_runs;

    let last_week_lobby_runs = app.daily.lobby_runs[app.daily.lobby_runs.length - 7]['total'];
    app.weekly.lobby_runs_change = app.totals.lobby_runs - last_week_lobby_runs;

    let last_week_finished_lobby_runs = app.daily.finished_lobby_runs[app.daily.finished_lobby_runs.length - 7]['total'];
    app.weekly.finished_lobby_runs_change = app.totals.finished_lobby_runs - last_week_finished_lobby_runs;
}

async function draw_player_graphs() {
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
}

async function draw_sprint_graphs() {
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
              borderColor: SPRINTS_COLOR,
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

async function draw_lobby_graphs() {
    new Chart("daily-lobbies", {
        type: 'line',
        data: {
          labels: app.daily.created_lobbies.map(({day}) => day),
          datasets: [{
              data: app.daily.created_lobbies.map(({total}) => total),
              label: "Total Lobbies Created",
              borderColor: LOBBIES_COLOR,
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

    new Chart("daily-new-lobbies", {
        type: 'line',
        data: {
          labels: app.daily.created_lobbies.map(({day}) => day),
          datasets: [{
              data: app.daily.created_lobbies.map(({daily_created_lobbies}) => daily_created_lobbies),
              label: "New Lobbies Created",
              borderColor: LOBBIES_COLOR,
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

    new Chart("daily-lobby-runs", {
        type: 'line',
        data: {
          labels: app.daily.lobby_runs.map(({day}) => day),
          datasets: [{
              data: app.daily.lobby_runs.map(({total}) => total),
              label: "Total Lobby Runs",
              borderColor: LOBBIES_COLOR,
              fill: false
            },
            {
                data: app.daily.finished_lobby_runs.map(({total}) => total),
                label: "Total Finished Lobby Runs",
                borderColor: LOBBIES_SUBCOLOR,
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

    new Chart("daily-new-lobby-runs", {
        type: 'line',
        data: {
          labels: app.daily.lobby_runs.map(({day}) => day),
          datasets: [{
              data: app.daily.lobby_runs.map(({daily_plays}) => daily_plays),
              label: "New Lobby Runs",
              borderColor: LOBBIES_COLOR,
              fill: false
            },
            {
                data: app.daily.finished_lobby_runs.map(({daily_plays}) => daily_plays),
                label: "New Finished Lobby Runs",
                borderColor: LOBBIES_SUBCOLOR,
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

    new Chart("daily-active-lobby-users", {
        type: 'line',
        data: {
          labels: app.daily.active_lobby_users.map(({day}) => day),
          datasets: [{
              data: app.daily.active_lobby_users.map(({active_users}) => active_users),
              label: "Users That Finished A Lobby Run",
              borderColor: LOBBIES_COLOR,
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

    new Chart("daily-average-lobby-user-plays", {
        type: 'line',
        data: {
          labels: app.daily.lobby_runs_per_user.map(({day}) => day),
          datasets: [{
              data: app.daily.lobby_runs_per_user.map(({lobby_runs_per_user}) => lobby_runs_per_user),
              label: "Average User Lobby Runs",
              borderColor: LOBBIES_COLOR,
              fill: false
            },
            {
                data: app.daily.finished_lobby_runs_per_user.map(({finished_lobby_runs_per_user}) => finished_lobby_runs_per_user),
                label: "Average Finished User Lobby Runs",
                borderColor: LOBBIES_SUBCOLOR,
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

async function draw_graphs() {
    await draw_player_graphs();
    draw_sprint_graphs();
    draw_lobby_graphs();
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
            finished_lobby_runs: 0,
            pct_goog_users: 0.0,
            pct_user_runs: 0.0,
            pct_user_finished_runs: 0.0,
            pct_user_marathons: 0.0,
            pct_user_finished_marathons: 0.0,
            daily_active_users: 0,
            weekly_active_users: 0,
            monthly_active_users: 0,
            daily_active_users_finished: 0,
            weekly_active_users_finished: 0,
            monthly_active_users_finished: 0,
        },
        weekly: {
            user_change: 0.0,
            runs_change: 0.0,
            finished_runs_change: 0.0,
            finished_lobby_runs_change: 0.0,
        },
        daily: {
            users: [],
            sprint_runs: [],
            finished_sprint_runs: [],
            sprint_runs_per_user: [],
            finished_sprint_runs_per_user: [],
            active_users: [],
            lobby_runs: [],
            finished_lobby_runs: [],
            created_lobbies: [],
            lobby_runs_per_user: [],
            finished_lobby_runs_per_user: [],
            active_lobby_users: []
        },
        active_tab: 'users',
        loading: false,
        load_time_sec: 0,
        last_updated: '',
        last_request_time: ''
    },
    methods: {
        is_active(tab_name) {
            return this.active_tab === tab_name
        },
        set_active(tab_name) {
            this.active_tab = tab_name
        },
        async poll_stats() {
            let response = await fetch("/api/stats/all");
            let res_json = await response.json();
            let last_updated = new Date(res_json['timestamp']);

            // Check if the most recently updated time is past the request time
            // Otherwise check again in 5 seconds
            if (last_updated >= this.last_request_time) {
                this.loading = false;
                window.location.reload();
                return;
            }

            setTimeout(this.poll_stats, 5 * 1000);
        },
        async refresh_stats(event) {
            try {
                const response = await fetchJson("/api/stats/calculate", 'GET');
                if (response.status === 200) {
                    alert("New stat calculation underway.");
                    this.last_request_time = new Date();
                    this.loading = true;
                    this.load_time_sec = 0;
                    this.countLoadTimer();
                } else if (response.status === 503) {
                    alert("Server currently processing stats! Check back in a bit.");
                }

                // Check in 30s to see if stats are done calculating
                setTimeout(this.poll_stats, 30 * 1000);
            } catch (e) {
                alert(e);
            }
        },
        countLoadTimer() {
            if (this.loading) {
                setTimeout(() => {
                    this.load_time_sec += 1
                    this.countLoadTimer()
                }, 1000)
            }
        }
    },

    created: async function () {
        await get_data();
        draw_graphs();
    }
});