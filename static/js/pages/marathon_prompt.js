import Vue from 'vue/dist/vue.esm.js';


const pg = serverData["pg"];
const sortMode = serverData["sortMode"];
const profile_name = serverData["profile_name"];

const runsPerPage = 10;

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        runs: [],
        username: '',
        totalpages: 0,
        page: 0,
        sortMode: sortMode,
        renderedRuns: []

    },

    methods: {

        getRuns: async function(username) {
            var response = await fetch("/api/marathon/" + username);

            if (response.status == 401) {
                alert(await response.text());
            }

            let resp = await response.json();

            if (this.sortMode === 'time') {
                resp.sort((a, b) => (a.total_time < b.total_time) ? 1 : ((a.total_time === b.total_time) ? ((a.path.length > b.path.length) ? 1 : -1) : -1))
            } else if (this.sortMode === 'path') {
                resp.sort((a, b) => (a.path.length < b.path.length) ? 1 : ((a.path.length === b.path.length) ? ((a.total_time < b.total_time) ? 1 : -1) : -1))
            }
            else if (this.sortMode === 'cp') {
                resp.sort((a, b) => (a.checkpoints.length < b.checkpoints.length) ? 1 : ((a.checkpoints.length === b.checkpoints.length) ? ((a.path.length < b.path.length) ? 1 : -1) : -1))
            }
            return resp
        },

        getPageNo: function () {
            if (this.runs.length === 0) {
                return 0;
            }
            return parseInt(pg)
        },

        buildNewLink: function (page) {
            let base = "/marathonruns/" + this.username + "?page=" + String(page)
            if (this.sortMode === 'path') {
                base += "&sort=path"
            } else if (this.sortMode === 'time') {
                base += "&sort=time"
            } else if (this.sortMode === 'cp') {
                base += "&sort=cp"
            }
            window.location.replace(base)
        },

        paginate: function () {
            const first = (pg-1) * runsPerPage
            const last = pg * runsPerPage
            for (let i = 0; i < this.runs.length; i++) {
                if (i >= first && i < last) {
                    this.renderedRuns.push(this.runs[i])
                }

            }
        },

        toggleSort: function(tab) {
            if (this.sortMode !== tab) {
                this.sortMode = tab
                this.buildNewLink(this.page)
            }
        },

        sortStatus: function(tab) {
            if (this.sortMode === tab) {
                return `<i class="bi bi-chevron-down"></i>`
            }
            return `<i class="bi bi-dash-lg"></i>`
        },


    },

    mounted: async function() {
        this.username = profile_name;
        this.runs = await this.getRuns(this.username);

        this.paginate();
        this.totalpages = Math.ceil(this.runs.length/runsPerPage);
        this.page = pg;
    }
})