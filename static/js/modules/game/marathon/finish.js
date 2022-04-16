
var FinishPage = {

    props: [
        "forfeited",
        "startArticle",
        "finalTime",
        "numVisitedUnique",
        "numCheckpointsVisited",
        "path",
        "activeCheckpoints",
        "promptId",
        "runId",
        "saved",
        "checkpointLimit",
        "username",
        "loggedIn"
    ],

    methods: {
        //copy sharable result
        copyResults: function(event) {
            let results = this.generateResults();
            document.getElementById("custom-tooltip").style.display = "inline";
            navigator.clipboard.writeText(results);
            setTimeout(function() {
                document.getElementById("custom-tooltip").style.display = "none";
            }, 1500);
        },


        //redirect to the corresponding prompt page
        finishPrompt: function(event) {
            window.location.replace("/marathonruns/" + this.username);
        },

        //go back to home page
        home: function (event) {
            window.location.replace("/");
        },


        generateResults: function(event) {

            let ranks = {
                0: "bruh 💀", //0
                3: "Wiki Noob ", //1-3
                6: "Wiki Apprentice", //4-6
                9: "Wiki Enjoyer", //7-9
                14: "Winner", //10-14
                20: "Tryhard", //15-19
                35: "Overachiever", //20-34
                100: "We didn't plan for anyone to get this far" //35+
            };

            let rank = "We didn't plan for anyone to get this far"
            for (const threshold in ranks) {
                if (this.numCheckpointsVisited <= threshold) {
                    rank = ranks[threshold];
                    break;
                }
            }

            return `Wiki Speedruns Marathon ${this.promptId}\n${this.startArticle}\n${this.numCheckpointsVisited} 🚩\nStatus: ${rank}`
        },

        genPathsToCheckpoints: function() {
            let el = document.getElementById("genPathsToCheckpoints");
            let newEl = document.createElement("p");
            newEl.innerHTML = "WIP... Stay Tuned!";

            el.parentNode.replaceChild(newEl, el);
        }

    },

    template: (
    `<div v-cloak class="text-left">
        <div v-if="!saved">
            <p v-if="!saved"><h4>Game Over! <span v-if="forfeited">You chose the easy way out.</span></h4></p>
            <p v-if="loggedIn">Your run was submitted to the leaderboard.</p>
            <p v-else>You are not logged in, but your run has been saved locally. Log in to upload your runs to your personal leaderboard!</p>
            <p><h4>Here's how you did:</h4></p>
        </div>
        <div v-else>
            <h4>Your progress has been saved to your browser!</h4>
            <p>You can access your local saved games from the home page.</p>
        </div>
        <div class="card md">
            <div class="card-body">
                <p><h4><strong class="font-italic">"{{startArticle}}"</strong></h4></p>
                <p>Time: <strong>{{(finalTime / 1000).toFixed(3)}} </strong>Seconds</p>
                <p>Number of unique articles visited: <strong>{{numVisitedUnique}}</strong></p>
                <p>Number of checkpoints visited: <strong>{{numCheckpointsVisited}}</strong></p>
                <p>The path you took: <br>{{path}}</p>
                <br/>
                <div v-if="!saved">
                    <div><p>Unfortunately, you weren't able to reach these checkpoints:</p><p>{{activeCheckpoints}}</p></div>
                    <div>
                        <button id="genPathsToCheckpoints" @click="genPathsToCheckpoints" class="btn btn-outline-secondary">See how you could've reached these</button>
                    </div>
                    <br/>
                    <div class="button-tooltip-container">
                        <button @click="copyResults" class="share-btn btn-1 btn-1c"><i class="bi bi-share"></i> Share</button>
                        <span id="custom-tooltip" ref="shareTooltip">Copied results to clipboard!</span>
                    </div>
                </div>
                <div><button @click="home" class="btn btn-outline-secondary">Return to home page</button></div>
                <br/>
                <div v-if="loggedIn"><button @click="finishPrompt" class="btn btn-outline-secondary">Check your marathon run history</button></div>
            </div>
        </div>
    </div>`
    )
};

export {FinishPage};
