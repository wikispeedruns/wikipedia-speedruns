var goalPage = "";
var timerInterval = null;
var startTime = 0;
var path = [];
var endTime = 0;

async function submitName(event)
{
    event.preventDefault();

    const reqBody = {
        "start_time": startTime,
        "end_time": endTime,
        "prompt_id": prompt_id,
        "path": path,
        "name": document.getElementById("name").value
    }

    // Send results to API
    try {
        const response = await fetch("/api/runs/create", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

        const run_id = await response.json();

        // Move to prompt page after 3 seconds
        window.location.href = "/prompt/" + prompt_id + "?run_id=" + run_id;

    } catch(e) {
        console.log(e);
    }

}

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
    }

    path.push(title)

    if (formatStr(title) === formatStr(goalPage)) {
        finish(); // No need to await this
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


    // Display finish stats and path
    Array.from(document.getElementsByClassName("finish")).forEach((el) => {
        el.style.display = "block";
    });
    document.getElementById("finishStats").innerHTML = "<p>You Found It! Final Time: " + (endTime - startTime)/1000 + "</p>";
    document.getElementById("path").innerHTML = "<p>" + formatPath(path) + "</p>";

    document.getElementById("submitName").addEventListener("submit", submitName);




}


function hideElements() {
    var hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar"]
    for(i=0; i<hide.length; i++) {
        var elements = document.getElementsByClassName(hide[i])
        //console.log("found: " + hide[i] + elements.length)
        for(j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
    }
    
    var id = ["See_also", "Notes_and_references", "Further_reading", "External_links", "References", "Notes", ];
    for(i=0; i<id.length; i++) {
        var e = document.getElementById(id[i]);
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


window.onload = async function() {
    const response = await fetch("/api/prompts/get/" + prompt_id);
    const prompt = await response.json();

    const article = prompt["start"];

    goalPage = prompt["end"];
    document.getElementById("guide").innerHTML = "Starting: " + article + " --> " + "Goal: " + goalPage
    loadPage(article)
}