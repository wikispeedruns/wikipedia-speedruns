async function getArticle(page, isMobile) {
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=1&format=json&origin=*&action=parse&prop=text&page=${page}${isMobile ? '&mobileformat=1' : ''}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    if ("error" in body) {
        return null;
    } else {
        return body["parse"];
    }
}

async function getArticleTitle(title) {
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=1&format=json&origin=*&action=parse&prop=displaytitle&page=${title}`, {
            mode: "cors"
        }
    )
    const body = await resp.json()

    if ("error" in body) {
        return null;
    } else {
        return body["parse"]["title"];
    }
}

async function getArticleSummary(page) {
    const resp = await fetch(
        `https://en.wikipedia.org/api/rest_v1/page/summary/${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    return body
}

export { getArticle, getArticleTitle, getArticleSummary };