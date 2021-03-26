
async function loadPage(page) {
    const resp = await fetch(
        `https://en.wikipedia.org/api/rest_v1/page/html/${page}?redirect=false`,
    )
    const body = await resp.text()
    console.log(body)
    document.getElementById("wikipedia-frame").innerHTML = body
}

function loadArticle() {
    const article = document.getElementById("article-input").value
    loadPage(article)
}

window.onload = function() {
    
}