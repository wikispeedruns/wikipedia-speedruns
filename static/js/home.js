
async function loadPage(page) {
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()
    console.log(body)
    console.log(body["parse"])
    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"]
}

function loadArticle() {
    const article = document.getElementById("article-input").value
    loadPage(article)
}

window.onload = function() {
    
}