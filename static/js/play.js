import { getRandTip } from "./modules/tooltips.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        startArticle: "",
        endArticle: "",
        timer: "",
        countdown: 8,
        finished: false,
        started: false,
        gunShow: false,
        activeTip: "",
        caught: false,
        path:[],
        finalTime:"",
        prompt_id: 0,

    },
    methods : {
        formatPath: function (pathArr) {
            output = "";
            for(i=0; i<pathArr.length - 1;i++) {
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
        }

    }
})



var goalPage = "";
var timerInterval = null;
var startTime = 0;
var path = [];
var endTime = 0;

var run_id = -1;

var keyMap = {};
var seconds;

var ctrlfwarnings = false;

function handleWikipediaLink(e) 
{
    e.preventDefault();
    const linkEl = e.currentTarget;

    if (linkEl.getAttribute("href").substring(0, 1) === "#") {
        var a = linkEl.getAttribute("href").substring(1);
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

    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    const title = body["parse"]["title"]

    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"]
    document.getElementById("title").innerHTML = "<h1><i>"+title+"</i></h1>"
    

    // Start timer if we are at the start
    if (path.length == 0) {
        startTime = Date.now()
        timerInterval = setInterval(displayTimer, 20);    

        const reqBody = {
            "start_time": startTime,
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
    
    path.push(title)

    if (formatStr(title) === formatStr(goalPage)) {
        await finish();
    }

    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideElements();
    window.scrollTo(0, 0)
}

async function finish() {

    app.$data.finished = true;
    app.$data.path = path;
    app.$data.finalTime = app.$data.timer;

    // Stop timer
    endTime = Date.now();
    clearInterval(timerInterval);
    //document.getElementById("timer").innerHTML="";

    // Prevent are you sure you want to leave prompt
    window.onbeforeunload = null;

    const reqBody = {
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

        //window.location.replace("/prompt/" + prompt_id + "?run_id=" + run_id);

    } catch(e) {
        console.log(e);
    }
}


function hideElements() {
    
    var hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar", "authority-control", "external", "sistersitebox"]
    for(var i=0; i<hide.length; i++) {
        var elements = document.getElementsByClassName(hide[i])
        //console.log("found: " + hide[i] + elements.length)
        for(var j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
    }
    
    var idS = ["See_also", "Notes_and_references", "Further_reading", "External_links", "References", "Notes", "Citations", "Explanatory_notes"];
    for(var i=0; i<idS.length; i++) {
        var e = document.getElementById(idS[i]);
        if (e !== null) {
            e.style.display = "none";
        }
    }

    //hide Disambig
    
    var elements = document.getElementsByClassName("hatnote");
    for (var i=0; i < elements.length; i++) {
        var a = elements[i].getElementsByClassName("mw-disambig");
        //console.log(a)
        if (a.length !== 0) {
            elements[i].style.display = "none";
        }
        //mw-disambig
    }

    //var all = document.getElementsByClassName("mw-parser-output")[0].querySelectorAll("h2", "div", "ul", "p");
    var all = document.getElementById("wikipedia-frame").querySelectorAll("h2, div, ul, p, h3");
    var flip = false
    for (var i = 0; i < all.length; i++) {
        if (!flip) {
            if (all[i].tagName == "H2") {
                //console.log("checking h2");
                var check = all[i].getElementsByClassName("mw-headline")
                if (check.length !== 0) {
                    //console.log(check[0].id)
                    for (var j = 0; j < idS.length; j++) {
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
    seconds = (Date.now() - startTime) / 1000;
    app.$data.timer = seconds;
    //document.getElementById("timer").innerHTML = "Elapsed Time<br/><strong>"+seconds + "s</strong>";
}



function countdownOnLoad(start, end) {


    app.$data.startArticle = start;
    app.$data.endArticle = end;

    app.$data.activeTip = getRandTip();

    var countDownStart = Date.now();
    var countDownTime = app.$data.countdown * 1000;

    var x = setInterval(function() {

        var now = Date.now()
      
        // Find the distance between now and the count down date
        var distance = countDownStart + countDownTime - now;

        app.$data.countdown = Math.floor(distance/1000)+1;

        if (distance < -1000) {
            clearInterval(x);

            app.$data.started = true;
            

            startTime = Date.now();
            ctrlfwarnings = true;

        }
        if (distance < 700 && distance > 610) {
            app.$data.gunShow = true;
        }
      }, 50);

      app.$data.gunShow = false;

}

function checkForFind(e) {

    console.log(e.code);
    e = e || event;
    keyMap[e.code] = e.type == 'keydown';
    if (keyMap["KeyF"] && (keyMap["ControlLeft"] || keyMap["ControlRight"])) {
        if (ctrlfwarnings == true) {

            app.$data.finished = true;
            app.$data.caught = true;
        }
    }
}


window.addEventListener("load", async function() {
    const response = await fetch("/api/prompts/" + prompt_id);

    app.$data.prompt_id = prompt_id;

    if (response.status != 200) {
        const error = await response.text();
        this.alert(error)
        // Prevent are your sure you want to leave prompt
        window.onbeforeunload = null;
        window.location.href = "/"   // TODO error page

    }

    const prompt = await response.json();
    const article = prompt["start"];

    goalPage = prompt["end"];

    await countdownOnLoad(article,goalPage);

    loadPage(article);
});

window.onbeforeunload = function() {
    return true;
};



window.addEventListener("keydown", function(e) {
    checkForFind(e);
});
window.addEventListener("keyup", function(e) {
    checkForFind(e);
});




