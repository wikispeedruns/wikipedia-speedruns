/*
Logic for Tutorial Page

The tutorial page has the same HUD as the normal play page, but with second
"dialog box" to display the hints. The logic is also different, rather
than getting the prompt and submitting a run, the prompt is hard coded
and nothing happens at the end.

*/

//JS module imports
import { ArticleRenderer } from "./modules/game/articleRenderer.js";
import { PagePreview } from "./modules/game/pagePreview.js";

/* Given a DOM element `element`, overlay a div with a transparent yellow
 * background temporarily
 */
function highlight(element) {
    // Reuse this div
    if (!highlight.div) {
        highlight.div = document.createElement('div');
        highlight.div.style.position = 'absolute';
        highlight.div.style.borderRadius = '8px';
        highlight.div.style.pointerEvents = 'none';
    }

    var div = highlight.div;

    div.style.transition = 'background 2s';
    div.style.backgroundColor = "rgba(241,231,64,.5)";


    const width = element.offsetWidth;
    const height = element.offsetHeight;

    div.style.width = (width + 8) + 'px';
    div.style.height = (height + 8) + 'px';
    div.style.zIndex = element.style.zIndex + 1;

    element.offsetParent.appendChild(div);

    div.style.left = element.offsetLeft + (width - div.offsetWidth) / 2 + 'px';
    div.style.top = element.offsetTop + (height - div.offsetHeight) / 2 + 'px';

    element.scrollIntoView();

    setTimeout(function() {
        div.style.transition = "background 2s";
        div.style.backgroundColor = "rgba(255,255,255,0)";
    }, 1000);
}

/* Component defining the content inside of the tutorial box
 * same for desktop and mobile currently
 */
Vue.component('tutorial-prompts', {

    data: function() {
        return {
            highlighting: false
        };
    },

    mounted: function() {
        this.highlightElement("#time-box");
    },

    methods: {
        highlightElement(selector) {
            let element = document.querySelector(selector);
            if (element) {
                highlight(element);
            }
        },

        next() {
            this.highlightElement(".infobox");
        },

        prev() {
            this.highlightElement("a[href=\"#History\"]");

        }
    },

    template: (`
    <div style="height: 100%; display: flex; flex-direction: column; ">

        <div style="flex-grow: 1">
            <p>
                Welcome to the Wikispeedruns tutorial!
            </p>
        </div>


        <div style="margin-left: auto; margin-top:auto !important; zIndex: 100000000">
            <a class="btn btn-outline-secondary" role="button" @click="prev">
                <i class="bi bi-chevron-left"></i>
            </a>
            <a class="btn btn-outline-secondary" role="button" @click="next">
                <i class="bi bi-chevron-right"></i>
            </a>
        </div>
    </div>
    `),
});


let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'page-preview': PagePreview
    },


    data: {
        startArticle: "United_States",
        endArticle: "Pennsylvania",
        currentArticle: "",
        path: [],

        startTime: null,
        elapsed: 0,
    },

    mounted: async function() {
        // Prevent accidental leaves
        window.onbeforeunload = () => true;

        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback, this.showPreview, this.hidePreview);

        this.renderer.loadPage("United_States");

        this.startTime = Date.now();
        setInterval(() => {
            const seconds = (Date.now() - this.startTime) / 1000;
            this.elapsed = seconds;
        }, 50);
    },


    methods : {
        pageCallback: function(page, loadTime) {
            this.hidePreview();

            // TODO make other links besides tutorial unclickable

            if (this.path.length == 0 || this.path[this.path.length - 1] != page) {
                this.path.push(page);
            }
            this.currentArticle = page;



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
