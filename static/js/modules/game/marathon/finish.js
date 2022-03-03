
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
        "checkpointLimit"
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
            window.location.replace("/marathonprompt/" + this.promptId + "?run_id=" + this.runId);
        },

        //go back to home page
        home: function (event) {
            window.location.replace("/");
        },


        generateResults: function(event) {
            return `WIP`
        },

        genPathsToCheckpoints: function() {
            let el = document.getElementById("genPathsToCheckpoints");
            let newEl = document.createElement("p");
            newEl.innerHTML = "WIP";

            el.parentNode.replaceChild(newEl, el);
        }

    },

    template: (
    `<div v-cloak class="text-left">
        <div v-if="!saved">
            <p v-if="!saved"><h4>Game Over! <span v-if="forfeited">You chose the easy way out.</span></h4></p>
            <p>Your run was submitted to the leaderboard.</p>
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
                    <div><button @click="finishPrompt" class="btn btn-outline-secondary">See the leaderboard</button></div>
                    <br/>
                </div>
                <div><button @click="home" class="btn btn-outline-secondary">Return to home page</button></div>
            </div>
        </div>
    </div>`
    )
};

export {FinishPage};