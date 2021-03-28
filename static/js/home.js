

function handleWikipediaLink(e) 
{
    e.preventDefault();
    const linkEl = e.currentTarget;
    
    // Disable the other links, otherwise we might load multiple links
    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = (e) => {
            e.preventDefault();
            console.log("prevent multiple click");
        };
    });

    // Ignore external links
    if (linkEl.getAttribute("rel") !== "mw:WikiLink") return;

    loadPage(linkEl.getAttribute("href"))
}

async function loadPage(page) {
    const resp = await fetch(
        `https://en.wikipedia.org/api/rest_v1/page/html/${page}?redirect=false`,
    )
    const body = await resp.text()
    document.getElementById("wikipedia-frame").innerHTML = body

    document.querySelectorAll("#wikipedia-frame a").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });
}

function loadArticle() {
    const article = document.getElementById("article-input").value
    loadPage(article)
}

window.onload = function() {
    
}