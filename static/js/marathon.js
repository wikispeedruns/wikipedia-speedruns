var timerInterval = null;
///var startTime = 0;
var path = [];
//var endTime = 0;


var defaultStartingClicks = 11;
var clicksPerCheckpoint = 5;

var clicksRemaining = defaultStartingClicks;

var seed = 0;


var checkpoints = [];

var visitedCheckpoints = [];
var uniqueArticlesVisited = 0;

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


async function getTitle(page) {
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    return body["parse"]["title"]
}

async function loadPage(page) {

    clicksRemaining -= 1;

    

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

    if (!path.includes(title)) {
        uniqueArticlesVisited += 1;
    }

    /*// Start timer if we are at the start
    if (path.length == 0) {
        startTime = Date.now()
        timerInterval = setInterval(displayTimer, 20);    
    }*/
    

    path.push(title)

    var hitcheckpoint = false;
    var checkpointindex = -1;
    reqBody = {'seed':seed};

    for (let i = 0; i < checkpoints.length; i++) {

        if (formatStr(title) === formatStr(checkpoints[i])) {
            clicksRemaining += clicksPerCheckpoint;

            //query for new checkpoint

            checkpointindex = i;
            hitcheckpoint = true;

            for (let j = 0; j < checkpoints.length; j++) {
                if (i !== j) {
                    reqBody["cp"+String(j)] = checkpoints[j]
                } else {
                    reqBody["cp"+String(i)] = title
                }
                
            }

            checkpoints[i] = "Generating a new checkpoint..."
            updateCounter();

            visitedCheckpoints.push(title);

        }
        
    }

    if (clicksRemaining === 0) {
        await finish();
    }


    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideElements();
    window.scrollTo(0, 0)

    updateCounter();

    if (hitcheckpoint) {
        console.log("hit checkpoint, generating new checkpoint")

        do {
            try {
                console.log(reqBody)
                const response = await fetch("/api/marathon/getcheckpoint/", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(reqBody)
                })

                const resp = await response.json();
                checkpoints[checkpointindex] = await getTitle(resp["checkpoint"]);

                console.log(checkpoints)
                console.log(resp)

            } catch(e) {
                console.log(e);
            }
        } while ( countocc(checkpoints[checkpointindex], checkpoints) > 1);
        
        updateCounter();
    }
}

function countocc(item, arr) {
    var count = 0;
    for (i=0; i<arr.length; i++) {
        if (item === arr[i]) {
            count++;
        }
    }
}

async function finish() {
    // Stop timer
    //endTime = Date.now();
    //clearInterval(timerInterval);
    //document.getElementById("timer").innerHTML="";

    // Prevent prompt
    window.onbeforeunload = null;

    console.log(visitedCheckpoints)

    const reqBody = {
        //"start_time": startTime,
        //"end_time": endTime,
        "prompt_id": prompt_id,
        "path": path,
        "checkpoints": visitedCheckpoints,
    }

    // Send results to API
    try {
        const response = await fetch("/api/marathon/runs/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

        const run_id = await response.json();

        console.log("Run saved");

        //window.location.href = "/prompt/" + prompt_id + "?run_id=" + run_id;

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


function formatStr(string) {
    return string.replace("_", " ").toLowerCase()
}

/*function displayTimer() {
    seconds = (Date.now() - startTime) / 1000;
    document.getElementById("timer").innerHTML = seconds + "s";
}*/

function getRandTip() {
    return "There are five permanent members of the UN security council: China, France, Russia, United Kingdom, and the United States."
}

function countdownOnLoad(start, checkpoints) {
    
    var guideBlock = document.getElementById("guide");
    var mainBlock = document.getElementById("main");
    var countdownBlock = document.getElementById("countdown");
    var tipsBlock = document.getElementById("tips");

    var gifBlock = document.getElementById("mirroredimgblock");

    var guide = "<strong>Starting article: </strong>" + start + "    -->    <strong>Checkpoints: </strong>";
    for(i=0; i<5; i++) {
        guide = guide + checkpoints[i];
        guide = guide + " | ";
    }

    guideBlock.innerHTML = guide;

    mainBlock.style.display = "none";
    countdownBlock.style.display = "block";
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
            //guideBlock.innerHTML = "<strong>" + start + "</strong> --> <strong>" + end + "</strong>";
            guideBlock.style.display = "none";
            tipsBlock.style.display = "none";
            gifBlock.style.display = "none";
            //startTime = Date.now();

        }
        if (distance < 700 && distance > 610) {
            gifBlock.style.visibility = "visible";
            gifBlock.appendChild(gunimg1);
            gifBlock.appendChild(gunimg2);
        }
      }, 50);

}


function updateCounter() {
    var counterBlock = document.getElementById("counter");

    while(counterBlock.firstChild){
        counterBlock.removeChild(counterBlock.firstChild);
    }

    counterBlock.style.display = "block";

    var b = document.createElement("div");
    b.innerHTML = "Clicks Remaining:";
    b.style.fontSize = "25px";
    
    var num = document.createElement("div");
    num.innerHTML = String(clicksRemaining);
    num.style.fontSize = "40px";

    var c = document.createElement("div");
    c.innerHTML = "Checkpoints:";
    c.style.fontSize = "25px";

    var checkpointList = document.createElement("ul");
    for(i=0; i<checkpoints.length; i++) {
        var a = document.createElement("li");
        a.innerHTML = checkpoints[i];
        checkpointList.appendChild(a);
    }


    var tip = document.createElement("div");
    tip.innerHTML = "Go as far as you can! Each article you visit will cost 1 click, but each checkpoint you visit will grant you an extra 5 clicks! Game will end when you run out of clicks";
    tip.style.fontSize = "15px";

    var articles = document.createElement("div");
    articles.innerHTML = "Articles visited:";
    articles.style.fontSize = "20px";

    var articlescount = document.createElement("div");
    articlescount.innerHTML = String(uniqueArticlesVisited);
    articlescount.style.fontSize = "40px";



    var visitedCheckpointsTitle = document.createElement("div");
    visitedCheckpointsTitle.innerHTML = "Checkpoints visited:";
    visitedCheckpointsTitle.style.fontSize = "20px";

    var visitedCheckpointsList = document.createElement("ul");
    for(i=0; i<visitedCheckpoints.length; i++) {
        var a = document.createElement("li");
        a.innerHTML = visitedCheckpoints[i];
        visitedCheckpointsList.appendChild(a);
    }

    counterBlock.appendChild(b)
    counterBlock.appendChild(num)
    counterBlock.appendChild(c)
    counterBlock.appendChild(checkpointList)
    counterBlock.appendChild(articles)
    counterBlock.appendChild(articlescount)
    counterBlock.appendChild(tip)
    counterBlock.appendChild(visitedCheckpointsTitle)
    counterBlock.appendChild(visitedCheckpointsList)
}

/*
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
}*/

window.addEventListener("load", async function() {
    const response = await fetch("/api/prompts/marathon/" + prompt_id);
    const prompt = await response.json();

    const article = prompt["start"];

    checkpoints.push(prompt["checkpoint1"]);
    checkpoints.push(prompt["checkpoint2"]);
    checkpoints.push(prompt["checkpoint3"]);
    checkpoints.push(prompt["checkpoint4"]);
    checkpoints.push(prompt["checkpoint5"]);
    seed = prompt["seed"];

    await countdownOnLoad(article,checkpoints);

    loadPage(article);
});

window.onbeforeunload = function() {
    return true;
};

/*
window.addEventListener("keydown", function(e) {
    checkForFind(e);
});
window.addEventListener("keyup", function(e) {
    checkForFind(e);
});
*/