/*
Logic for Tutorial Page

The tutorial page has the same HUD as the normal play page, but with second
"dialog box" to display the hints. The logic is also different, rather
than getting the prompt and submitting a run, the prompt is hard coded
and nothing happens at the end.

TODO maybe freeze the articles so wikipedia changing doesn't break this

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

    props: [
        "currentArticle"
    ],

    data: function() {
        return {
            // Support mobile swipes
            // TODO maybe just make the entire box into 2 seciotns
            touchStartX: 0,

            curStep: 0,

            // defines the tutorial
            tutorial: [
                {
                    text: "Welcome to the WikiSpeedruns Tutorial"
                },
                {
                    text: "Look at the infobox!",
                    highlight: ".infobox"
                },
                {
                    text: "Remember to use the Table of Contents. Try \"Political divisions\"!",
                    highlight: "a[href=\"#Political_divisions\"]"
                },
                {
                    text: "Try clicking on \"North America\"!",
                    requiredLink: "North_America"
                },
                {
                    text: "Congratulations, you've finished!",
                }
            ]
        };
    },

    mounted: function() {
    },

    watch: {
        currentArticle: function(newVal, oldVal) {
            console.log(oldVal + "->" + newVal);
        }
    },

    methods: {
        highlightElement(selector) {
            let element = document.querySelector(selector);
            if (element) {
                highlight(element);
            }
        },

        // TODO prevent if we are waiting for a link? Or maybe call articleRender.loadPage()?
        next() {
            this.curStep++;
            const step = this.tutorial[this.curStep]

            // TODO handle end
            if (!step) return;

            if (step.highlight) {
                this.highlightElement(this.tutorial[this.curStep].highlight);
            }

            if (step.requiredLink) {
                // Highlight the link
                const selector = `a[href=\"/wiki/${step.requiredLink}\"]`
                this.highlightElement(selector);

                // Set onclick to use the handler provided by the articleRenderer
                // but also calls next
                // See pageCallback of main vue function
                let linkEl = document.querySelector(selector);
                linkEl.onclick = (e) => {
                    this.next();
                    linkEl.originalOnClick(e);
                }
            }

        },

        prev() {
            if (this.curStep > 0) this.curStep--;
        },

        handleTouchStart(e) {
            e.preventDefault();
            this.touchStartX = e.changedTouches[0].screenX;
        },

        handleTouchEnd(e) {
            e.preventDefault();
            const endX = e.changedTouches[0].screenX;

            if (endX <= this.touchStartX - 80) {
                this.next(); //swiping left
            }
            if (endX >= this.touchStartX + 80) {
                this.prev(); // swiping right
            }
        },
    },

    template: (`
    <div
        v-on:touchstart="handleTouchStart"
        v-on:touchend="handleTouchEnd"
        style="height: 100%; display: flex; flex-direction: column; ">

        <div style="flex-grow: 1">
            <template v-for="(step, index) in tutorial">
                <p v-if="index == curStep"> {{step.text}} </p>
            </template>

            <p class="show-on-mobile" v-if="curStep == 0"> Swipe left/right at the bottom of the page to navigate </p>
        </div>

        <div class="show-on-desktop">
            <div style="margin-left: auto; margin-top:auto !important; zIndex: 100000000">
                <a class="btn btn-outline-secondary" role="button" @click="prev">
                    <i class="bi bi-chevron-left"></i>
                </a>
                <a class="btn btn-outline-secondary" role="button" @click="next">
                    <i class="bi bi-chevron-right"></i>
                </a>
            </div>
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
            let frame = document.getElementById("wikipedia-frame");

            frame.querySelectorAll("a, area").forEach((el) => {
                // Don't prevent users from using TOC links
                if (el.getAttribute("href") && el.getAttribute("href").substring(0, 1)  === "#") {
                    return;
                }
                // Store the original handler so we can use it later
                el.originalOnClick = el.onclick;

                el.onclick = (e) => {
                    e.preventDefault();
                    // TODO put a real alert here, maybe in tutorial box.
                    // i.e. set a "wrong link clicked prop" so the tutorial can flash a message
                    alert("Not yet");
                };
            });


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
