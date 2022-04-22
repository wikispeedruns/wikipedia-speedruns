/* play.js is core of processing gameplay. This includes everything from retrieving information about a prompt,
countdown to start, loading of each wikipedia page, parsing and filtering wikipedia links, processing game logic,
and submitting runs.

With the new Marathon game mode, many of these components are being reused with different game logic. So many of
these components should be as modular/generic as possible.
*/

//JS module imports
import { ArticleRenderer } from "./modules/game/articleRenderer.js";
import { PagePreview } from "./modules/game/pagePreview.js";


Vue.component('tutorial-prompts', {
    template: (`
    <div>
        <p>
        Welcome to the Wikispeedruns tutorial!
        </p>


    </div>
    `),
});


//Vue container. This contains data, rendering flags, and functions tied to game logic and rendering. See play.html
let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'page-preview': PagePreview
    },


    data: {
        startArticle: "",    // For all game modes, this is the first article to load
        endArticle: "",      // For sprint games. Reaching this article will trigger game finishing sequence
        currentArticle: "",
        path: [],             // array to store the user's current path so far, submitted with run

        startTime: null,     //For all game modes, the start time of run (mm elapsed since January 1, 1970)
        endTime: null,       //For all game modes, the end time of run (mm elapsed since January 1, 1970)
        elapsed: 0,
        timerInterval: null,

        finished: false,     //Flag for whether a game has finished, used for rendering
        started: false,      //Flag for whether a game has started (countdown finished), used for rendering

        loggedIn: false,
    },

    mounted: async function() {
        // Prevent accidental leaves
        window.onbeforeunload = () => true;

        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback, this.showPreview, this.hidePreview);

        this.renderer.loadPage("United_States");

    },


    methods : {
        pageCallback: function(page, loadTime) {

            this.hidePreview();
            // Game logic for sprint mode:

            if (this.path.length == 0 || this.path[this.path.length - 1] != page) {
                this.path.push(page);
            }

            this.currentArticle = page;

            this.startTime += loadTime;

            //if the page's title matches that of the end article, finish the game, and submit the run
            if (page === this.endArticle) {
                this.finish();
            }

        },


        showPreview: function(e) {
            this.$refs.pagePreview.showPreview(e);
        },
        hidePreview: function(e) {
            this.$refs.pagePreview.hidePreview(e);
        }
    },



})


// Disable find hotkeys, players will be given a warning
window.addEventListener("keydown", function(e) {
    //disable find
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) {
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
});
