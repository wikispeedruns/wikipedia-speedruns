
var FinishPage = {

    props: [
        "promptId",
        "runId",

        "startArticle",
        "endArticle",
        "finalTime",
        "path"
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
            window.location.replace("/prompt/" + this.promptId + "?run_id=" + this.runId);
        },

        //go back to home page
        home: function (event) {
            window.location.replace("/");
        },


        generateResults: function(event) {
            return `Wiki Speedruns ${this.promptId}
            ${this.startArticle}
            ${this.path.length - 1} 🖱️
            ${(this.finalTime) / 1000} ⏱️`
        },

    },

    template: (`
    <div v-cloak class="text-left">
        <p><h4>You found it!</h4></p>
        <p>Your run was submitted to the leaderboard.</p>
        <p><h4>Here's how you did:</h4></p>
        <div class="card md">
            <div class="card-body">
                <p><h4><strong class="font-italic">"{{startArticle}}"</strong> to <strong class="font-italic">"{{endArticle}}"</strong></h4></p>
                <p>Time: <strong>{{finalTime/1000}} </strong>Seconds</p>
                <p>Number of links visited: <strong>{{path.length-1}}</strong></p>
                <p>The path you took: <br>{{path}}</p>
                <div class="button-tooltip-container">
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
