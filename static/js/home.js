var goalPage;
var start = 1;
var startTime;
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
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()
    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"]
    
    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    if (start === 1) {
        start = 0;
        const startTime = Date.now();
    }
}


function loadArticle() {
    const article = document.getElementById("start-article").value
    const goalPage = document.getElementById("goal-article").value
    document.getElementById("guide").innerHTML = "Starting: " + article + " --> " + "Goal: " + goalPage
    loadPage(article)
}

window.onload = function() {
    
}