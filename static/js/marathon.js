import { serverData } from "./modules/serverData.js"
import { fetchJson } from "./modules/fetch.js";

const prompt_id = serverData["prompt_id"];

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        startArticle: "",
        timer: "",
        countdown: 8,
        finished: false,
        started: false,
        gunShow: false,
        activeTip: "",
        path:[],
        finalTime:"",
        prompt_id: 0,
        
        checkpoints:[],
        activeCheckpoints: [],
        visitedCheckpoints: [],
        numVisitedUnique: 0,
        clicksRemaining: 3,
    },
    computed: {
        numCheckpointsVisited : function () {
            return this.visitedCheckpoints.length
        },
    },
    methods : {
        formatPath: function (pathArr) {
            let output = "";
            for(let i=0; i<pathArr.length - 1;i++) {
                output = output.concat(pathArr[i])
                output = output.concat(" -> ")
            }
            output = output.concat(pathArr[pathArr.length - 1])
            return output;
        }, 

        finishPrompt: function (event) {
            window.location.replace("/marathonprompt/" + prompt_id);
        }, 

        home: function (event) {
            window.location.replace("/");
        }

    }
})

var timerInterval = null;

var keyMap = {};

const clicksPerCheckpoint = 5;

var startTime = 0;

function handleWikipediaLink(e) 
{
    e.preventDefault();
    const linkEl = e.currentTarget;

    if (linkEl.getAttribute("href").substring(0, 1) === "#") {
        let a = linkEl.getAttribute("href").substring(1);
        //console.log(a);
        document.getElementById(a).scrollIntoView();

    } else {

        // Ignore external links
        if (linkEl.getAttribute("href").substring(0, 6) !== "/wiki/") return;

        // Disable the other links, otherwise we might load multiple links
        document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
            el.onclick = (e) => {
                e.preventDefault();
                console.log("prevent multiple click");
            };
        });

        // Remove "/wiki/" from string
        loadPage(linkEl.getAttribute("href").substring(6))
    }
}

async function loadPage(page) {

    app.$data.clicksRemaining -= 1;

    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    const title = body["parse"]["title"]

    let frameBody = document.getElementById("wikipedia-frame")
    frameBody.innerHTML = body["parse"]["text"]["*"]
    frameBody.querySelectorAll("a").forEach(function(a) {
        a.innerHTML = '<div style="display:inline-block">' + a.text.split('').map(function(character) {
            return '<div style="display:inline-block">' + character.replace(/\s/g, '&nbsp;') + '</div>'
        }).join('') + '</div>'
    });

    document.getElementById("title").innerHTML = "<h1><i>"+title+"</i></h1>"
    
    if (!app.$data.path.includes(title)) {
        app.$data.numVisitedUnique += 1;
    }

    // Start timer if we are at the start
    if (app.$data.path.length == 0) {
        startTime = Date.now()
        timerInterval = setInterval(displayTimer, 20);    
    }
    
    app.$data.path.push(title)

    var hitcheckpoint = false;
    var checkpointindex = -1;

    for (let i = 0; i < app.$data.activeCheckpoints.length; i++) {

        if (formatStr(title) === formatStr(app.$data.activeCheckpoints[i])) {
            app.$data.clicksRemaining += clicksPerCheckpoint;

            //query for new checkpoint

            checkpointindex = i;
            hitcheckpoint = true;

            app.$data.visitedCheckpoints.push(title);

        }
        
    }


    if (app.$data.clicksRemaining === 0) {
        await finish();
    }

    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideElements();
    window.scrollTo(0, 0)

    
    if (hitcheckpoint) {
        console.log("hit checkpoint, getting new checkpoint")

        console.log(app.$data.activeCheckpoints[checkpointindex])

        let got = false

        app.$data.checkpoints.forEach(bucket => {
            if (bucket.length> 0 && !got) {
                let el = bucket.pop()
                app.$data.activeCheckpoints[checkpointindex] = el['a']
                console.log(el['a'])
                got = true
            }
        })
    }

    console.log(app.$data)
}

async function finish() {

    app.$data.finished = true;
    app.$data.finalTime = app.$data.timer;

    // Stop timer
    clearInterval(timerInterval);

    // Prevent are you sure you want to leave prompt
    window.onbeforeunload = null;

    // Send results to API
    try {
        const response = await fetchJson(`/api/marathon/runs/`, "POST", {
            path: JSON.stringify(app.$data.path),
            checkpoints: JSON.stringify(app.$data.visitedCheckpoints),
            prompt_id: String(app.$data.prompt_id)
        }
        )

        console.log("run saved")

    } catch(e) {
        console.log(e);
    }
}


function hideElements() {
    
    const hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar", "authority-control", "external", "sistersitebox"]
    for(let i=0; i<hide.length; i++) {
        let elements = document.getElementsByClassName(hide[i])
        //console.log("found: " + hide[i] + elements.length)
        for(let j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
    }
    
    const idS = ["See_also", "Notes_and_references", "Further_reading", "External_links", "References", "Notes", "Citations", "Explanatory_notes"];
    for(let i=0; i<idS.length; i++) {
        let e = document.getElementById(idS[i]);
        if (e !== null) {
            e.style.display = "none";
        }
    }

    //hide Disambig
    
    let elements = document.getElementsByClassName("hatnote");
    for (let i=0; i < elements.length; i++) {
        let a = elements[i].getElementsByClassName("mw-disambig");
        //console.log(a)
        if (a.length !== 0) {
            elements[i].style.display = "none";
        }
        //mw-disambig
    }

    //let all = document.getElementsByClassName("mw-parser-output")[0].querySelectorAll("h2", "div", "ul", "p");
    let all = document.getElementById("wikipedia-frame").querySelectorAll("h2, div, ul, p, h3");
    let flip = false
    for (let i = 0; i < all.length; i++) {
        if (!flip) {
            if (all[i].tagName == "H2") {
                //console.log("checking h2");
                let check = all[i].getElementsByClassName("mw-headline")
                if (check.length !== 0) {
                    //console.log(check[0].id)
                    for (let j = 0; j < idS.length; j++) {
                        if (check[0].id == idS[j]) {
                            //console.log("found see also at: " + i);
                            all[i].style.display = "none";
                            flip = true;
                        }
                    }
                }
            }
        } else {
            all[i].style.display = "none";
        }
    }
    
}

function formatStr(string) {
    return string.replace("_", " ").toLowerCase()
}

function displayTimer() {
    const seconds = (Date.now() - startTime) / 1000;
    app.$data.timer = seconds;
}

function getRandTip() {
    const tips = [
        "There are five permanent members of the UN security council: China, France, Russia, United Kingdom, and the United States.",
        "The Fortune magazine has a list for top 500 United States companies (“Fortune 500”), as well as a list for top 500 global companies (“Fortune Global 500”).",
        "Brazil is currently the world’s largest producer of sugarcane, and by a lot!",
        "Buddhism originated in ancient India sometime between the 6th and 4th centuries BCE.",
        "Pressing the back button will forfeit your attempt!",
        "Infoboxes on the right often give very quick and useful links, especially for biographical and geographical pages.",
        "Plan ahead, but be flexible! If you foresee a better route than what you had planned, go for it!",
        "Use the Table of Contents to your advantage!",
        "Some article subsections have an associated main article, usually linked under the subsection title."
    ];

    return tips[Math.floor(Math.random() * tips.length)];
}

function countdownOnLoad() {

    app.$data.activeTip = getRandTip();

    let countDownStart = Date.now();
    let countDownTime = app.$data.countdown * 1000;

    let x = setInterval(function() {

        let now = Date.now()
      
        // Find the distance between now and the count down date
        let distance = countDownStart + countDownTime - now;

        app.$data.countdown = Math.floor(distance/1000)+1;

        if (distance < -1000) {
            clearInterval(x);

            app.$data.started = true;
            

            startTime = Date.now();
        }
        if (distance < 700 && distance > 610) {
            app.$data.gunShow = true;
        }
      }, 50);

      app.$data.gunShow = false;

}

function disableFind(e) {
    console.log(e);
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) { 
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.")
    }
}

window.addEventListener("load", async function() {
    const response = await fetch("/api/marathon/prompt/" + prompt_id);

    app.$data.prompt_id = prompt_id;

    if (response.status != 200) {
        const error = await response.text();
        this.alert(error)
        // Prevent are your sure you want to leave prompt
        window.onbeforeunload = null;
        window.location.href = "/"   // TODO error page

    }

    const prompt = await response.json();

    console.log(prompt)

    app.$data.startArticle = prompt['start'];
    app.$data.activeCheckpoints = JSON.parse(prompt['initcheckpoints']);
    app.$data.checkpoints = JSON.parse(prompt['checkpoints']);

    await countdownOnLoad();

    loadPage(app.$data.startArticle);
});

window.onbeforeunload = function() {
    return true;
};

window.addEventListener("keydown", function(e) {
    disableFind(e);
});
