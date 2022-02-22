import { getRandTip } from "./modules/tooltips.js";
import { serverData } from "./modules/serverData.js"

const prompt_id = serverData["prompt_id"];

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        startArticle: "",
        endArticle: "",
        timer: "",
        countdown: 8,
        finished: false,
        started: false,
        activeTip: "",
        path:[],
        finalTime:"",
        prompt_id: 0,
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
            window.location.replace("/prompt/" + prompt_id + "?run_id=" + run_id);
        }, 

        home: function (event) {
            window.location.replace("/");
        },

        copyResults: function(event) {
            let results = generateResultText();
            document.getElementById("custom-tooltip").style.display = "inline";
            navigator.clipboard.writeText(results);
            setTimeout(function() {
                document.getElementById("custom-tooltip").style.display = "none";
            }, 1500);
        },
    }
})



let goalPage = "";
let timerInterval = null;
let startTime = 0;
let path = [];
let endTime = 0;

let run_id = -1;

let seconds;
let keyMap = {};

function handleWikipediaLink(e) 
{
    e.preventDefault();

    const linkEl = e.currentTarget;

    if (linkEl.getAttribute("href").substring(0, 1) === "#") {
        let a = linkEl.getAttribute("href").substring(1);
        //console.log(a);
        document.getElementById(a).scrollIntoView();

    } else {

        // Ignore external links and internal file links
        if (!linkEl.getAttribute("href").startsWith("/wiki/") || linkEl.getAttribute("href").startsWith("/wiki/File:")) {
            return;
        }

        // Disable the other linksto prevent multiple clicks
        document.querySelectorAll("#wikipedia-frame a, #wikipedia-frame area").forEach((el) =>{
            el.onclick = (e) => {
                e.preventDefault();
                console.log("prevent multiple click");
            };
        });

        // Remove "/wiki/" from string
        loadPageWrapper(linkEl.getAttribute("href").substring(6))
    }
}

async function loadPageWrapper(page) {
    try {
        await loadPage(page)
    } catch (error) {
        // Reenable all links if loadPage fails
        document.querySelectorAll("#wikipedia-frame a, #wikipedia-frame area").forEach((el) =>{
            el.onclick = handleWikipediaLink;
        });
    }
}

async function loadPage(page) {

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
        let iter = document.createNodeIterator(a, NodeFilter.SHOW_TEXT);
        let textNode;
        while (textNode = iter.nextNode()) {
            let replacementNode = document.createElement('div');
            replacementNode.innerHTML = '<div style="display:inline-block">' + textNode.textContent.split('').map(function(character) {
                return '<div style="display:inline-block">' + character.replace(/\s/g, '&nbsp;') + '</div>'
            }).join('') + '</div>'
            textNode.parentNode.insertBefore(replacementNode.firstChild, textNode);
            textNode.parentNode.removeChild(textNode);
        }
    });

    document.getElementById("title").innerHTML = "<h1><i>"+title+"</i></h1>"
    
    path.push(title)

    if (formatStr(title) === formatStr(goalPage)) {
        await finish();
    }

    document.querySelectorAll("#wikipedia-frame a, #wikipedia-frame area").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideElements();
    setMargin();
    window.scrollTo(0, 0)
}

async function finish() {

    app.$data.finished = true;
    app.$data.path = path;
    app.$data.finalTime = app.$data.timer;

    // Stop timer
    clearInterval(timerInterval);
    endTime = startTime + app.$data.finalTime*1000;

    // Prevent are you sure you want to leave prompt
    window.onbeforeunload = null;

    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "path": path,
    }

    // Send results to API
    try {
        const response = await fetch(`/api/runs/${run_id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

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
        if (a.length !== 0) {
            elements[i].style.display = "none";
        }
    }

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

function setMargin() {
    const element = document.getElementById("time-box");
    console.log(element.offsetHeight + 25)
    document.getElementById("wikipedia-frame").firstChild.style.paddingBottom = (element.offsetHeight + 25) +"px";
}

function formatStr(string) {
    return string.replace("_", " ").toLowerCase()
}

function displayTimer() {
    const seconds = (Date.now() - startTime) / 1000;
    app.$data.timer = seconds;
}

// Race condition between countdown timer and "immediate start" button click
// Resolves when either condition resolves
async function countdownOnLoad(start, end) {

    app.$data.startArticle = start;
    app.$data.endArticle = end;

    app.$data.activeTip = getRandTip();

    let countDownStart = Date.now();
    let countDownTime = app.$data.countdown * 1000;

    document.getElementById("mirroredimgblock").classList.toggle("invisible");

    // Condition 1: countdown timer
    const promise1 = new Promise(resolve => {
        const x = setInterval(function() {
            const now = Date.now()
          
            // Find the distance between now and the count down date
            let distance = countDownStart + countDownTime - now;
            app.$data.countdown = Math.floor(distance/1000)+1;

            if (distance <= 0) {
                resolve();
                clearInterval(x);
            }

            if (distance < 700 && distance > 610 && document.getElementById("mirroredimgblock").classList.contains("invisible")) {                
                document.getElementById("mirroredimgblock").classList.toggle("invisible")
            }

        }, 50);
    });

    // Condition 2: "immediate start" button click
    const promise2 = new Promise(r =>
        document.getElementById("start-btn").addEventListener("click", r, {once: true})
    )

    await Promise.any([promise1, promise2]);
}

async function saveRun() {
    const reqBody = {
        "prompt_id": prompt_id,
    }

    try {
        const response = await fetch("/api/runs", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

        run_id = await response.json();

    } catch(e) {
        console.log(e);
    }
}

function disableFind(e) {
    if ([114, 191, 222].includes(e.keyCode) || ((e.ctrlKey || e.metaKey) && e.keyCode == 70)) { 
        e.preventDefault();
        this.alert("WARNING: Attempt to Find in page. This will be recorded.");
    }
}

function startGame() {
    app.$data.started = true;
    startTime = Date.now();
    timerInterval = setInterval(displayTimer, 20);
}

function generateResultText() {
    return `Wiki Speedruns ${prompt_id}
${app.$data.startArticle}
${path.length - 1} 🖱️
${(endTime - startTime) / 1000} ⏱️`
}

window.addEventListener("load", async function() {
    const response = await fetch("/api/sprints/" + prompt_id);

    app.$data.prompt_id = prompt_id;

    if (response.status != 200) {
        const error = await response.text();
        this.alert(error)
        // Prevent are your sure you want to leave prompt
        window.onbeforeunload = null;
        window.location.replace("/");   // TODO error page

    }

    const prompt = await response.json();
    const article = prompt["start"];
    goalPage = prompt["end"];
    saveRun(); // Save run on clicking "play" when `prompt_id` is valid

    // Wait for countdown to expire AND the start article elements to load before starting the timer and displaying the page
    await Promise.all([countdownOnLoad(article, goalPage), loadPage(article)]);

    startGame();
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    setMargin();
});

window.onbeforeunload = function() {
    return true;
};

window.addEventListener("keydown", function(e) {
    disableFind(e);
});
