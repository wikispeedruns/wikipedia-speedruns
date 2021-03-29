var goalPage = "";
var start = 1;
var startTime = 0;

function handleWikipediaLink(e) 
{
    e.preventDefault();
    const linkEl = e.currentTarget;
    
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

async function loadPage(page) {
    
    console.log(page)
    console.log(goalPage)

    if (page === goalPage) {
        totalTime = (Date.now() - startTime)/1000;
        showFinish();
        document.getElementById("finishStats").innerHTML = "Final Time: " + totalTime;
    }

    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    // TODO add Article Title ("firstHeading")

    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"]
    
    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideElements();
    hideStart();

    if (start === 1) {
        start = 0;
        startTime = Date.now();
        console.log(startTime)
    }
}

function getTitle() {
    
}

function hideElements() {
    var hide = ["reference","mw-editsection","reflist","portal","refbegin"]
    for(i=0; i<hide.length; i++) {
        var elements = document.getElementsByClassName(hide[i])
        console.log("found: " + hide[i] + elements.length)
        for(j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
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

window.onload = function() {
    
}