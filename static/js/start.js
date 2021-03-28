var goalPage = "";
var start = 1;
var startTime = 0;
var totalTime = 0;

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
    }

    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()
    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"]
    
    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    hideStart();

    if (start === 1) {
        start = 0;
        startTime = Date.now();
        console.log(startTime)
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
    document.getElementById("finishStats").innerHTML = "Final Time: " + totalTime;
}

function loadStart() {
    const article = document.getElementById("start-article").value
    goalPage = document.getElementById("goal-article").value
    loadPage(article)
    document.getElementById("guide").innerHTML = "Starting: " + article + " --> " + "Goal: " + goalPage
}

window.onload = function() {
    
}