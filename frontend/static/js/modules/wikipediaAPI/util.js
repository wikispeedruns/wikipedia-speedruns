const WIKIPEDIA_RETRY_STATUSES = new Set([408, 425, 429, 500, 502, 503, 504]);
const wikipediaJsonCache = new Map();

// This is an async delay used between retries. Awaiting it does not block the UI thread.
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRetryDelayMs(response, attempt) {
    const retryAfterHeader = response.headers.get("retry-after");
    const retryAfterSeconds = retryAfterHeader ? parseInt(retryAfterHeader, 10) : NaN;
    if (!Number.isNaN(retryAfterSeconds) && retryAfterSeconds >= 0) {
        return retryAfterSeconds * 1000;
    }

    return 500 * (attempt + 1);
}

// `retries=2` means up to 3 total attempts. `useCache` reuses identical JSON responses
// within the current page session for stable lookups like titles and summaries.
async function fetchWikipediaJson(url, { retries = 2, useCache = true } = {}) {
    if (useCache && wikipediaJsonCache.has(url)) {
        return wikipediaJsonCache.get(url);
    }

    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const response = await fetch(url, { mode: "cors" });
            if (response.ok) {
                const body = await response.json();
                if (useCache) {
                    wikipediaJsonCache.set(url, body);
                }
                return body;
            }

            console.warn("Wikipedia request failed:", response.status, url);

            if (!WIKIPEDIA_RETRY_STATUSES.has(response.status) || attempt === retries) {
                return null;
            }

            await sleep(getRetryDelayMs(response, attempt));
        } catch (error) {
            console.warn("Wikipedia request threw:", url, error);
            if (attempt === retries) {
                return null;
            }

            await sleep(500 * (attempt + 1));
        }
    }

    return null;
}

async function getArticle(page, isMobile = false, lang = 'en', revisionDate=null) {
    // Encode to safely handle spaces/quotes in titles for API requests.
    const encodedPage = encodeURIComponent(page);
    let url = `https://${lang}.wikipedia.org/w/api.php?redirects=1&disableeditsection=true&format=json&origin=*&action=parse&prop=text&useskin=vector`;

    if (isMobile) {
        url += "&mobileformat=1";
    }


    // If given a reivision date (string), use that to query the last revision before the given date.
    if (revisionDate) {

        // Encode revision date for query params; fall back to current page if lookup fails.
        const encodedRevisionDate = encodeURIComponent(revisionDate);
        let revisionurl = `https://${lang}.wikipedia.org/w/api.php?action=query&format=json&origin=*&prop=revisions&redirects=1&titles=${encodedPage}`
            + `&formatversion=2&rvdir=older&rvprop=timestamp|ids&rvlimit=1&rvstart=${encodedRevisionDate}`;

        const body = await fetchWikipediaJson(revisionurl, { retries: 0 });

        if (!body || "error" in body) {
            return null;
        }

        const page = body?.query?.pages?.[0];
        const revision = page?.revisions?.[0];

        if (!revision || !revision.revid) {
            url += `&page=${encodedPage}`;
        } else {
            url += `&oldid=${revision.revid}`;
        }
    } else {
        url += `&page=${encodedPage}`;
    }

    const body = await fetchWikipediaJson(url, { retries: 0 })

    if (!body || "error" in body) {
        return null;
    } else {
        return body["parse"];
    }
}

async function getArticleTitle(title, lang = 'en') {
    // Use query+redirects for a canonical title without fetching full HTML.
    const encodedTitle = encodeURIComponent(title);
    const body = await fetchWikipediaJson(
        `https://${lang}.wikipedia.org/w/api.php?action=query&redirects=1&origin=*&format=json&formatversion=2&titles=${encodedTitle}`
    );

    // Guard against missing/invalid responses from the API.
    if (!body || !body.query || !body.query.pages || !body.query.pages[0]) {
        return null;
    }
    if (body.query.pages[0].missing) return null;
    return body.query.pages[0].title;
}

async function articleCheck(title, lang = 'en') {
    const body = await fetchWikipediaJson(
        `https://${lang}.wikipedia.org/w/api.php?action=query&origin=*&format=json&prop=pageprops&ppprop=disambiguation&titles=${title}&formatversion=2`,
        { useCache: false }
    );

    if (!body || !body.query || !body.query.pages || !body.query.pages[0]) {
        return {warning: "Unable to validate that article right now. Please try again."};
    }

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
    // Summary endpoints still use the page title in the URL path, so encode it first.
    let decodedPage = page;
    try {
        decodedPage = decodeURIComponent(page);
    } catch (error) {
        // If the title was already raw or contains a stray `%`, keep the original string.
    }

    const encodedPage = encodeURIComponent(decodedPage);
    const body = await fetchWikipediaJson(
        `https://${lang}.wikipedia.org/api/rest_v1/page/summary/${encodedPage}`
    );

    return body
}

async function getAutoCompleteArticles(search, lang = 'en', numEntries = 5){
    // https://en.wikipedia.org/w/api.php?action=opensearch&format=json&formatversion=2&search=a&namespace=0&limit=10
    // Encode user input before adding it to the query string.
    const encodedSearch = encodeURIComponent(search);
    let body = await fetchWikipediaJson(
        `https://${lang}.wikipedia.org/w/api.php?action=opensearch&origin=*&format=json&formatversion=2&search=${encodedSearch}&namespace=0&limit=${numEntries}`,
        { useCache: false }
    );
    if (!body) {
        return [];
    }
    body = body[1]; // get the list of araticles
    return body;
}

async function getSupportedLanguages() {
    let body = await fetchWikipediaJson(
        'https://www.mediawiki.org/w/api.php?action=sitematrix&origin=*&format=json&smtype=language&formatversion=2'
    );
    if (!body) {
        return [];
    }

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
    const body = await fetchWikipediaJson(
        `https://${lang}.wikipedia.org/w/api.php?action=query&origin=*&format=json&list=random&formatversion=2&rnnamespace=0&rnlimit=1`,
        { useCache: false }
    );
    if (!body || !body.query || !body.query.random || !body.query.random[0]) {
        return null;
    }
    return body['query']['random'][0]['title'];
}

export { getArticle, getArticleTitle, getArticleSummary, articleCheck, checkArticles, getAutoCompleteArticles, getSupportedLanguages, getRandomArticle };
