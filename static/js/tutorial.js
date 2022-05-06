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

    element.scrollIntoView(true);

    setTimeout(function() {
        div.style.transition = "background 2s";
        div.style.backgroundColor = "rgba(255,255,255,0)";
    }, 1000);
}

/* Component defining the content inside of the tutorial box
 * same for desktop and mobile currently
 */
Vue.component('tutorial', {

    props: [
        "currentArticle"
    ],

    data: function() {
        return {
            // Support mobile swipes
            // TODO maybe just make the entire box into 2 sections and tap?
            touchStartX: 0,

            curStep: 0,

            message: "",

            // defines the tutorial
            // highlight: takes a query selector and highlights the element
            // requried link: takes a link href (look at actual href) and enables that link. when clicked
            //                 the article will be loaded and the next step is loaded.
            tutorial: [
                {
                    text: "Welcome to the WikiSpeedruns Tutorial!"
                },
                {
                    text: "The goal of the game is to get from one Wikipedia page to another as \
                           fast as possible by clicking the links in the page",
                },
                {
                    text: "It is also fun to try and use as few clicks as possible!",
                },
                // {
                //     text: "The goal article, time, and number of clicks are all shown in the HUD",
                //     highlight: "#time-box"
                // },
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

    watch: {
        currentArticle(newArticle, oldArticle) {
            // Make other links besides tutorial unclickable
            let frame = document.getElementById("wikipedia-frame");

            frame.querySelectorAll("a, area").forEach((el) => {
                // Don't prevent users from using TOC links
                if (!el.getAttribute("href") || el.getAttribute("href").substring(0, 1)  === "#") {
                    return;
                }

                // Store the original handler so we can use it later
                el.originalOnClick = el.onclick;
                const linkTitle = el.getAttribute("href").substring(6);

                // User can only cause link to load page if it is the required link on links
                el.onclick = (e) => {
                    e.preventDefault();

                    if (linkTitle === this.tutorial[this.curStep].requiredLink) {
                        // Call the original onclick (provided by ArticleRenderer) to load the next page
                        el.originalOnClick(e);
                        this.next();
                    } else if (this.tutorial[this.curStep].requiredLink) {
                        this.flashMessage("Please click the suggested link");
                    } else {
                        this.flashMessage("Please read this tutorial first");
                    }

                };
            });
        }
    },

    methods: {

        flashMessage(message) {
            this.message = message;
            setTimeout(() => {
                // Check so we don't overwrite a different message
                if (this.message === message) {
                    this.message = "";
                }
            }, 2000);
        },

        highlightElement(selector) {
            let element = document.querySelector(selector);
            if (element) {
                highlight(element);
            }
        },

        next() {
            if (this.curStep === this.tutorial.length - 1) {
                return;
            }

            // Increment
            this.curStep++;
            const step = this.tutorial[this.curStep]

            if (step.highlight) {
                this.highlightElement(step.highlight);
            }

            if (step.requiredLink) {
                // Highlight the link
                const selector = `a[href=\"/wiki/${step.requiredLink}\"]`
                this.highlightElement(selector);
            }

            // Disable are you sure you want to leave warning
            if (this.curStep === this.tutorial.length - 1) {
                window.onbeforeunload = () => false;
            }
        },

        prev() {
            if (this.curStep > 0)  {
                this.curStep--;
            }
        },

        handleTouchStart(e) {
            this.touchStartX = e.changedTouches[0].screenX;
        },

        handleTouchEnd(e) {
            const endX = e.changedTouches[0].screenX;
            if (endX <= this.touchStartX - 80) {
                if (this.tutorial[this.curStep].requiredLink) {
                    this.flashMessage("Click the link to continue!");
                    return;
                }
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

            <!-- Message if something goes wrong -->
            <p v-if="message" class="text-danger">
                {{message}}
            </p>
            <template v-else v-for="(step, index) in tutorial">
                <p v-if="index == curStep"> {{step.text}} </p>
            </template>

            <p class="show-on-mobile" v-if="curStep == 0"> Swipe left/right at the bottom of the page to navigate </p>

            <p v-if="curStep === this.tutorial.length - 1"> <a href="/">Click here to go home</a> </p>
        </div>

        <div class="show-on-desktop">
            <div style="margin-left: auto; margin-top:auto !important;">
                <button v-bind:disabled="curStep === 0"
                        @click="prev"
                        class="btn btn-outline-secondary">
                    <i class="bi bi-chevron-left"></i>
                </button>
                <button v-bind:disabled="curStep === tutorial.length - 1  || tutorial[curStep].requiredLink"
                        @click="next"
                        class="btn btn-outline-secondary" >
                    <i class="bi bi-chevron-right"></i>
                </button>
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

        isMobile: false
    },

    mounted: async function() {
        // used to only render one version of tutorial
        this.isMobile = window.screen.width < 768;

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
