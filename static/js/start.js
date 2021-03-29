var goalPage = "";
var start = 1;
var finished = 0;
var startTime = 0;
var path = [];

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
    
    if (start === 1) {
        start = 0;
        startTime = Date.now();
    }

    const title = body["parse"]["title"]

    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"]
    document.getElementById("title").innerHTML = "<h1><i>"+title+"</i></h1>"

    if (finished === 0) {
        path.push(title)
    }

    if (formatStr(title) === formatStr(goalPage)) {
        totalTime = (Date.now() - startTime)/1000;
        showFinish();
        document.getElementById("finishStats").innerHTML = "<p>You Found It! Final Time: " + totalTime + "</p>";
        document.getElementById("path").innerHTML = "<p>" + formatPath(path) + "</p>";
        finished = 1;
    }

    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideElements();
    hideStart();
    window.scrollTo(0, 0)

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

function hideStart() {
    document.getElementById("starting").style.display = "none"
    document.getElementById("guide").style.display = "block"
}

function showFinish() {
    var cols = document.getElementsByClassName("finish");
    for(i=0; i<cols.length; i++) {
      cols[i].style.display = "block";
    }
    
}

function loadStart() {
    const article = document.getElementById("start-article").value
    goalPage = document.getElementById("goal-article").value
    
    loadPage(article)

    document.getElementById("guide").innerHTML = "Starting: " + article + " --> " + "Goal: " + goalPage
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

window.onload = function() {
}