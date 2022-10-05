/*
Logic for Tutorial Page

The tutorial page has the same HUD as the normal play page, but with second
"dialog box" to display the hints. The logic is also different, rather
than getting the prompt and submitting a run, the prompt is hard coded
and nothing happens at the end.

TODO maybe freeze the articles so wikipedia changing doesn't break this
TODO going back too far (i.e. after a page has been clicked breaks it)

*/

// JS module imports
import Vue from 'vue/dist/vue.esm.js';

import { ArticleRenderer } from "../modules/game/articleRenderer.js";
import { PagePreview } from "../modules/game/pagePreview.js";

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

    // We need to handle the highlighting within a table specially
    let parent = element.offsetParent;
    if (parent.tagName === "TD") {
        // Add wrapper around element
        let wrapper = document.createElement('div');
        wrapper.style.position = "relative"

        element.parentNode.insertBefore(wrapper, element);
        wrapper.appendChild(element);

        // Use wrapper div as positioning parent
        parent = wrapper;
    }

    parent.appendChild(div);



    div.style.left = element.offsetLeft + (width - div.offsetWidth) / 2 + 'px';
    div.style.top = element.offsetTop + (height - div.offsetHeight) / 2 + 'px';

    element.scrollIntoView(true);

    setTimeout(function() {
        div.style.transition = "background 2s";
        div.style.backgroundColor = "rgba(255,255,255,0)";
    }, 1000);
}

const beforeUnloadListener = (event) => {
    event.preventDefault();
    return event.returnValue = "Are you sure you want to exit? Your progess will be lost";
};

/* Component defining the content inside of the tutorial box
 * same for desktop and mobile currently
 */
Vue.component('tutorial', {

    props: [
        "isMobile",
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
            // requiredLink: takes a link href (look at actual href) and enables that link. when clicked
            //                 the article will be loaded and the next step is loaded.
            // currentArticle: A hint for if the user goes back to load the previous article
            tutorial: [
                {
                    text: "Welcome to the WikiSpeedruns Tutorial!",
                    highlight: ".HUD"
                },
                {
                    text: "The goal of the game is to get from one Wikipedia page to another as \
                           fast as possible by clicking the links in the page.",
                },
                {
                    text: "It's also fun to try and use as few clicks as possible!",
                },
                {
                    text: "The goal article, time, and number of clicks are all shown in the HUD.",
                    highlight: "#time-box"
                },
                {
                    text: "Fun Fact: 'Walt Whitman' to 'Walt Disney', was the first prompt ever released on WikiSpeedruns.",
                },
                {
                    text: "Before you get started, let's go over a few basic rules."
                },
                {
                    text: "1. Any link shown on the page is fair game. Note though that some links (e.g. disambiguation links) have been removed."
                },
                {
                    text: "2. Using any sort of find in page through your browser is prohibited."
                },
                {
                    text: "3. Going back is not allowed, you have to find your way back by clicking links! Going back \
                           in the browser will just quit the game."
                },
                {
                    text: "Now let's think about how to get to 'Walt Disney'."
                },
                {
                    text: "You can view a preview of the 'Walt Disney' page by hovering over the ⓘ next to the goal article.",
                    highlight: "#timebox-preview"
                },
                {
                    text: "As shown in the preview, Walt Disney is a famous American cultural figure, so maybe we can find him in the 'United States' page."
                },
                {
                    text: "Let's try getting there through 'Long Island'.",
                    requiredLink: "Long_Island",
                    currentArticle: "Walt_Whitman"
                },
                {
                    text: "Now we have to find a link to the 'United States'.",
                },
                {
                    text: "Links in infobox or summaries are also valid, and a good place to find general information.",
                    highlight: ".infobox"
                },
                {
                    text: "For example, we can find the the link to the 'United States' article here.",
                    requiredLink: "United_States",
                    currentArticle: "Long_Island"
                },
                {
                    text: "Hint: It's often good to think about a 'hub' page from where you can navigate to the goal article easily.\
                           'United States' is often a good one."
                },
                {
                    text: "Although you can't use the browser find, you can still use the table of contents.",
                },
                {
                    text: "Walt Disney is probably most famous for his movies, so let's try the cinema section.",
                    highlight: "a[href=\"#Cinema\"]"
                },
                {
                    text: "There is \'Walt Disney\'!",
                    requiredLink: "Walt_Disney",
                    currentArticle: "United_States"
                },
                {
                    text: "Thank you for playing the tutorial, and have fun!",
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
                        this.flashMessage(`Please click '${this.tutorial[this.curStep].requiredLink.replace("_", "  ")}' to continue`);
                    } else {
                        this.flashMessage("Please read this tutorial first");
                    }

                };
            });
        }
    },

    mounted: function() {
        this.highlightElement("#tutorial");
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

            // Disable are you sure you want to leave
            if (this.curStep === this.tutorial.length - 1) {
                window.removeEventListener("beforeunload", beforeUnloadListener);
            }
        },

        prev() {
            if (this.curStep > 0)  {
                this.curStep--;
            }

            const step = this.tutorial[this.curStep]

            // If the previous step was a different article, trigger a event
            // to load the previous page
            if (step.currentArticle) {
                this.$emit('change-article', step.currentArticle);

                // Highlight after the page loads
                if (step.requiredLink) {
                    const selector = `a[href=\"/wiki/${step.requiredLink}\"]`;
                    setTimeout(() => {this.highlightElement(selector)}, 1000);
                }
            }

            if (step.highlight) {
                this.highlightElement(step.highlight);
            }
        },


        handleTouchStart(e) {
            // bit of a hack
            // don't prevent default on the last message, so users can click on the link
            if (this.curStep !== this.tutorial.length - 1) {
                e.preventDefault();
            }

            this.touchStartX = e.changedTouches[0].screenX;
        },

        handleTouchEnd(e) {
            const endX = e.changedTouches[0].screenX;
            if (endX <= this.touchStartX - 60) {
                if (this.tutorial[this.curStep].requiredLink) {
                    this.flashMessage(`Click '${this.tutorial[this.curStep].requiredLink.replace("_", "  ")}' to continue!`);
                    return;
                }
                this.next(); //swiping left
            }
            if (endX >= this.touchStartX + 60) {
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


            <p v-if="curStep === this.tutorial.length - 1"> <a href="/">Click here to go home</a> </p>
        </div>


        <div v-if="isMobile && curStep == 0">
            Swipe left/right here (at the bottom of the page) to navigate
            <!-- https://lottiefiles.com/7635-swipe-left -->
            <img style="margin-left: auto; margin-right:auto; height:50px; width: 50px" src="/static/assets/swipe.gif">
        </div>


        <div v-if="!isMobile" style="margin-left: auto; margin-top:auto !important;">
            <button v-bind:disabled="curStep === 0"
                    @click="prev"
                    class="btn btn-primary">
                <i class="bi bi-chevron-left"></i>
            </button>
            <button v-bind:disabled="curStep === tutorial.length - 1  || tutorial[curStep].requiredLink"
                    @click="next"
                    class="btn btn-primary" >
                <i class="bi bi-chevron-right"></i>
            </button>
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
        startArticle: "Walt Whitman",
        endArticle: "Walt Disney",
        currentArticle: "",
        path: [],

        startTime: null,
        elapsed: 0,

        isMobile: false
    },

    mounted: async function() {
        // used to only render one version of tutorial
        this.isMobile = window.screen.width < 768;

        this.renderer = new ArticleRenderer(document.getElementById("wikipedia-frame"), this.pageCallback, this.showPreview, this.hidePreview);

        this.renderer.loadPage("Walt Whitman");

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

// Prevent accidental leaves
window.addEventListener("beforeunload", beforeUnloadListener);

// Disable find hotkeys, players will be given a warning
window.addEventListener("keydown", function(e) {
    //disable find
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) {
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
});
