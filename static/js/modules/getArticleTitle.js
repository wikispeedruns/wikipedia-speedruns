async function getArticleTitle(title) {
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${title}`, {
            mode: "cors"
        }
    )
    const body = await resp.json()

    let t =  body["parse"]["title"];

    return t
}

export { getArticleTitle };

