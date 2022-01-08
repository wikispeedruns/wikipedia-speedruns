var goalPage = "";
var timerInterval = null;
var startTime = 0;
var path = [];
var endTime = 0;

var run_id = -1;

var keyMap = {};

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
    // Stop timer
    endTime = Date.now();
    clearInterval(timerInterval);
    document.getElementById("timer").innerHTML="";

    // Prevent prompt
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

        window.location.href = "/prompt/" + prompt_id + "?run_id=" + run_id;

    } catch(e) {
        console.log(e);
    }
}


function hideElements() {
    
    var hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar", "authority-control", "external", "sistersitebox"]
    for(i=0; i<hide.length; i++) {
        var elements = document.getElementsByClassName(hide[i])
        //console.log("found: " + hide[i] + elements.length)
        for(j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
    }
    
    var idS = ["See_also", "Notes_and_references", "Further_reading", "External_links", "References", "Notes", "Citations", "Explanatory_notes"];
    for(i=0; i<idS.length; i++) {
        var e = document.getElementById(idS[i]);
        if (e !== null) {
            e.style.display = "none";
        }
    }

    //hide Disambig
    
    var elements = document.getElementsByClassName("hatnote");
    for (i=0; i < elements.length; i++) {
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
    for (i = 0; i < all.length; i++) {
        if (!flip) {
            if (all[i].tagName == "H2") {
                //console.log("checking h2");
                var check = all[i].getElementsByClassName("mw-headline")
                if (check.length !== 0) {
                    //console.log(check[0].id)
                    for (j = 0; j < idS.length; j++) {
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

function formatPath(pathArr) {
    output = "";
    for(i=0; i<pathArr.length - 1;i++) {
        output = output.concat(pathArr[i])
        output = output.concat(" -><br>")
    }
    output = output.concat(pathArr[pathArr.length - 1])
    return output;
}

function formatStr(string) {
    return string.replace("_", " ").toLowerCase()
}

function displayTimer() {
    seconds = (Date.now() - startTime) / 1000;
    document.getElementById("timer").innerHTML = seconds + "s";
}

function getRandTip() {
    return "There are five permanent members of the UN security council: China, France, Russia, United Kingdom, and the United States."
}

function countdownOnLoad(start, end) {
    
    var guideBlock = document.getElementById("guide");
    var mainBlock = document.getElementById("main");
    var countdownBlock = document.getElementById("countdown");
    var timerBlock = document.getElementById("timer");
    var tipsBlock = document.getElementById("tips");

    var gifBlock = document.getElementById("mirroredimgblock");

    guideBlock.innerHTML = "<strong>Starting article: </strong>" + start + "    -->    <strong>Goal article: </strong>" + end

    mainBlock.style.display = "none";
    countdownBlock.style.display = "block";
    timerBlock.style.display = "none";
    tipsBlock.style.display = "block";


    tipsBlock.innerHTML = getRandTip();

    //countdownBlock.innerHTML = "Prompt will begin in " + "5" + " seconds";
    /*    <img class="startgun" src="{{url_for('static', filename='assets/startgun.gif')}}">
    <img class="startgun invgif" src="{{url_for('static', filename='assets/startgun.gif')}}">
    */

    var countDownStart = Date.now();
    var countDownTime = 8000;


    var gunimg1 = document.createElement('img');
    var gunimg2 = document.createElement('img');
    imgpath = "/static/assets/startgun.gif";

    gunimg1.classList.add("startgun");
    gunimg2.classList.add("startgun");
    gunimg2.classList.add("invgif");
    gunimg2.src = imgpath;
    gunimg1.src = imgpath;


    var x = setInterval(function() {

        var now = Date.now()
      
        // Find the distance between now and the count down date
        var distance = countDownStart + countDownTime - now;
        //console.log(distance);
        //console.log(String(Math.floor(distance/1000)+1));
        countdownBlock.innerHTML = String(Math.floor(distance/1000)+1);
        countdownBlock.style.visibility = "visible";
        if (distance < -1000) {
            clearInterval(x);
            mainBlock.style.display = "block";
            countdownBlock.style.display = "none";
            guideBlock.innerHTML = "<strong>" + start + "</strong> --> <strong>" + end + "</strong>";
            timerBlock.style.display = "block";
            tipsBlock.style.display = "none";
            gifBlock.style.display = "none";
            startTime = Date.now();
            ctrlfwarnings = true;

        }
        if (distance < 700 && distance > 610) {
            gifBlock.style.visibility = "visible";
            gifBlock.appendChild(gunimg1);
            gifBlock.appendChild(gunimg2);
        }
      }, 50);

}

function checkForFind(e) {

    var guideBlock = document.getElementById("guide");
    var mainBlock = document.getElementById("main");
    var timerBlock = document.getElementById("timer");

    console.log(e.code);
    e = e || event;
    keyMap[e.code] = e.type == 'keydown';
    if (keyMap["KeyF"] && (keyMap["ControlLeft"] || keyMap["ControlRight"])) {
        if (ctrlfwarnings == true) {
            //ctrlfwarnings = 1;
            mainBlock.style.display = "none";
            timerBlock.style.display = "none";
            guideBlock.innerHTML = "STOP! You violated the law. Pay the court a fine or serve your sentence."
            var tesguard = document.createElement('img');
            tesguard.src = "/static/assets/stop.jpg";
            tesguard.width= "700";
            tesguard.style.marginTop = "40px";
            guideBlock.appendChild(tesguard);
        }
    }
}

window.addEventListener("load", async function() {
    const response = await fetch("/api/prompts/" + prompt_id);

    if (response.status != 200) {
        const error = await response.text();
        this.alert(error)
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