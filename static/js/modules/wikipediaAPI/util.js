async function getArticle(page, isMobile = false, lang = 'en') {
    const resp = await fetch(
        `https://${lang}.wikipedia.org/w/api.php?redirects=1&disableeditsection=true&format=json&origin=*&action=parse&prop=text&useskin=vector&page=${page}${isMobile ? '&mobileformat=1' : ''}`,
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

async function getArticleTitle(title, lang = 'en') {
    const resp = await fetch(
        `https://${lang}.wikipedia.org/w/api.php?redirects=1&format=json&origin=*&action=parse&prop=displaytitle&page=${title}`, {
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

async function articleCheck(title, lang = 'en') {
    const resp = await fetch(
        `https://${lang}.wikipedia.org/w/api.php?action=query&origin=*&format=json&prop=pageprops&ppprop=disambiguation&titles=${title}&formatversion=2`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json();

    if (body['query']['pages'][0]['ns'] !== 0) {
        return {warning: `ERROR: \'${title}\' is a namespaced article, may be impossible to reach. Please choose a different end article.`}
    }

    if (body['query']['pages'][0]['pageprops']) {
        return {warning: `ERROR: \'${title}\' is a disambiguation page and may be impossible to reach. Try checking the full title of the intended article on Wikipedia.`}
    }

    return {}
}

async function checkArticles(start, end, lang = 'en') {
    const resp = {body: {}};

    if(!start || !end){
        resp.err = "Prompt is currently empty";
        return resp;
    }

    resp.body.lang = lang;

    resp.body.start = await getArticleTitle(start, lang);
    if (!resp.body.start) {
        resp.err = `"${start}" is not a Wikipedia article`;
        return resp;
    }

    resp.body.end = await getArticleTitle(end, lang);
    if (!resp.body.end) {
        resp.err = `"${end}" is not a Wikipedia article`;
        return resp;
    }

    if(resp.body.start === resp.body.end) {
        resp.err = "The start and end articles are the same";
        return resp;
    }

    const checkRes = await articleCheck(resp.body.end, lang);
    if ('warning' in checkRes) {
        resp.err = checkRes["warning"];
        return resp;
    }

    return resp;
}

async function getArticleSummary(page, lang = 'en') {
    const resp = await fetch(
        `https://${lang}.wikipedia.org/api/rest_v1/page/summary/${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    return body
}

async function getAutoCompleteArticles(search, lang = 'en', numEntries = 5){
    // https://en.wikipedia.org/w/api.php?action=opensearch&format=json&formatversion=2&search=a&namespace=0&limit=10
    const resp = await fetch(
        `https://${lang}.wikipedia.org/w/api.php?action=opensearch&origin=*&format=json&formatversion=2&search=${search}&namespace=0&limit=${numEntries}`,
        {
            mode: "cors"
        }
    )
    let body = await resp.json();
    body = body[1]; // get the list of araticles
    return body;
}

async function getSupportedLanguages() {
    const resp = await fetch(
        'https://www.mediawiki.org/w/api.php?action=sitematrix&origin=*&format=json&smtype=language&formatversion=2',
        {
            mode: "cors"
        }
    )
    let body = await resp.json();

    body = body['sitematrix'];
    delete body['count'];

    let langs = [];

    for (const [, langprop] of Object.entries(body)) {
        if (langprop.code && langprop.site) {
            for (const siteprop of langprop.site) {
                if (siteprop.code === 'wiki') {
                    langs.push( {
                        "code": langprop.code,
                        "name": langprop.name
                    });
                    break;
                }
            }
        }
    }

    return langs;
}

async function getRandomArticle(lang = 'en') {
    const resp = await fetch(
        `https://${lang}.wikipedia.org/w/api.php?action=query&origin=*&format=json&list=random&formatversion=2&rnnamespace=0&rnlimit=1`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json();
    return body['query']['random'][0]['title'];
}

export { getArticle, getArticleTitle, getArticleSummary, articleCheck, checkArticles, getAutoCompleteArticles, getSupportedLanguages, getRandomArticle };
