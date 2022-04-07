
var FinishPage = {

    props: [
        "promptId",
        "lobbyId",
        "runId",

        "startArticle",
        "endArticle",
        "finalTime",
        "path",

        "loggedIn",
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
        finishPrompt: function (event) {
            if (this.lobbyId) {
                window.location.replace(`/lobby/${this.lobbyId}/prompt/${this.promptId}?run_id=${this.runId}`);
            } else {
                window.location.replace(`/prompt/${this.promptId}?run_id=${this.runId}`);
            }
        },

        //go back to home page
        home: function (event) {
            if (this.lobbyId) {
                window.location.replace(`/lobby/${this.lobbyId}`);
            } else {
                window.location.replace("/");
            }
        },


        generateResults: function(event) {
            return `Wiki Speedruns ${this.promptId}\n${this.startArticle}\n${this.path.length - 1} 🖱️\n${(this.finalTime) / 1000} ⏱️`
        },

    },

    template: (`
    <div v-cloak class="text-left">
        <p><h4>You found it!</h4></p>
        <p v-if="loggedIn">Your run was submitted to the leaderboard.</p>
        <p v-else>You are not logged in, but your run has been saved locally. Log in to upload your runs to the leaderboard!</p>
        <p><h4>Here's how you did:</h4></p>
        <div class="card md">
            <div class="card-body">
                <p><h4><strong class="font-italic">"{{startArticle}}"</strong> to <strong class="font-italic">"{{endArticle}}"</strong></h4></p>
                <p>Time: <strong>{{(finalTime / 1000).toFixed(3)}} </strong>Seconds</p>
                <p>Number of links visited: <strong>{{path.length-1}}</strong></p>
                <p>The path you took: <br>{{path}}</p>

                <div v-if="!lobbyId" class="button-tooltip-container">
                    <button @click="copyResults" class="share-btn btn-1 btn-1c"><i class="bi bi-share"></i> Share</button>
                    <span id="custom-tooltip" ref="shareTooltip">Copied results to clipboard!</span>
                </div>

                <div><button @click="finishPrompt" class="btn btn-outline-secondary">See the leaderboard</button></div>
                <br/>
                <div><button @click="home" class="btn btn-outline-secondary">Return to home page</button></div>
            </div>
        </div>
    </div>
    `)
};

export {FinishPage};
