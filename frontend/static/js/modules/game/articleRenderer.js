import { getArticle } from "../wikipediaAPI/util.js";

export class ArticleRenderer {

    /* frame: DOM element (i.e. through getElementById) to render article in
     * pageCallback: Called upon loading an article, should expect new page and load time
     *
     * mouseEnter, mouseLeave: function handlers for hovering over links (i.e. to display a preview)
     *
     * loadCallback: callback when page is started to load, lets callers add time
     *
     * revisionDate: date for article revisions are tied to.
     */
    constructor(frame, pageCallback, mouseEnter, mouseLeave, loadCallback, language, revisionDate) {
        this.frame = frame;
        this.frame.classList.add("wiki-insert");

        this.pageCallback = pageCallback;
        this.loadCallback = loadCallback;
        this.mouseEnter = mouseEnter;
        this.mouseLeave = mouseLeave;
        this.language = language;

        this.revisionDate = revisionDate;
        this.isLoadingPage = false;
    }

    async loadPage(page) {

        const isMobile = window.screen.width < 768;
        const startTime = Date.now();
        let body = null;

        if (this.loadCallback) {
            this.loadCallback();
        }

        try {
            body = await getArticle(page, isMobile, this.language, this.revisionDate);
        } catch (error) {
            console.error("Failed to fetch article:", page, error);
            renderLoadFailure(this.frame);
            return false;
        }

        try {
            // Render error message if article failed to load
            if (!body || !body["text"] || !body["title"]) {
                console.warn("Failed to load article:", page);
                renderLoadFailure(this.frame);
                return false;
            }
            // This is all in a try because something was throwing errors here, most likely because
            // we don't handle the wikipedia HTML correctly in some edge cases. This is a blanket solution
            // that just makes sure the essential functions work. Really, we should try and find the root cause
            // and fix that. However, we have not been able to reproduce it.
            // TODO add some sort of frontend eror montiroing so we can figure it out

            this.frame.innerHTML = body["text"]["*"];

            // Create title
            let titleEl = document.createElement("div");
            titleEl.innerHTML = "<h1><i>" + body["title"] + "</i></h1>";
            this.frame.prepend(titleEl);

            // Create end
            let endArticleEl = document.createElement("div");
            endArticleEl.innerHTML = `<hr class="mt-5"><h3 class="text-center">END</h3><hr>`
            this.frame.append(endArticleEl);

            if (isMobile) {
                disableLazyLoading(this.frame);
            }
            hideElements(this.frame);
            stripNonArticleLinks(this.frame);

        } catch (error) {
            console.error("Error rendering in page somewhere:", error)
            console.error(error)
        }

        this.frame.querySelectorAll("a, area").forEach((el) => {
            // Load href here so inspect element can't change link destination
            const href = el.getAttribute("href");

            // Arrow function to prevent 'this' from being overwritten
            el.onclick = (e) => {
                e.preventDefault();
                void this.handleWikipediaLink(href);
            }
            el.removeAttribute("title");

            if (this.mouseEnter && this.mouseLeave && !isMobile && isNormalWikipediaArticleLink(href)) {
                el.onmouseenter = this.mouseEnter;
                el.onmouseleave = this.mouseLeave;
            }
        });

        this.pageCallback(body["title"], Date.now() - startTime);

        return true;

    }


    async handleWikipediaLink(href) {
        if (!href) {
            return;
        }

        if (href.substring(0, 1) === "#") {
            let a = href.substring(1);
            document.getElementById(a)?.scrollIntoView();

        } else {
            if (!isNormalWikipediaArticleLink(href) || this.isLoadingPage) {
                return;
            }

            // Remove "/wiki/" from string
            let pageName = href.substring(6)
            if (pageName.includes("#")) {
                pageName = pageName.split("#")[0];
            }
            
            try {
                pageName = decodeURIComponent(pageName);
            } catch (error) {
                console.warn("Failed to decode page name:", pageName, error);
            }

            this.isLoadingPage = true;
            try {
                await this.loadPage(pageName);
            } finally {
                this.isLoadingPage = false;
            }
        }
    }
}

function disableLazyLoading(frame) {
    frame.querySelectorAll('.lazy-image-placeholder').forEach(el => {
        el.remove();
    });
    frame.querySelectorAll('noscript').forEach(el => {
        el.outerHTML = el.innerHTML;
    });
}

function hideElements(frame) {

    const hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar", "authority-control", "external", "sistersitebox", "box-More_citations_needed"]
    for(let i=0; i<hide.length; i++) {
        let elements = document.getElementsByClassName(hide[i])
        //console.log("found: " + hide[i] + elements.length)
        for(let j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
    }

    const idS = ["See_also", "Notes_and_references", "Further_reading", "External_links", "References", "Notes", "Citations", "Explanatory_notes"];
    for(let i=0; i<idS.length; i++) {
        let e = document.getElementById(idS[i]);
        if (e !== null) {
            e.style.display = "none";
        }
    }

    // hide Disambig - Disabled hide by community request

    // let elements = document.getElementsByClassName("hatnote");
    // for (let i=0; i < elements.length; i++) {
    //     let a = elements[i].getElementsByClassName("mw-disambig");
    //     if (a.length !== 0) {
    //         elements[i].style.display = "none";
    //     }
    // }

    let all = frame.querySelectorAll("h2, div, ul, p, h3");
    let flip = false
    for (let i = 0; i < all.length; i++) {
        if (!flip) {
            if (all[i].tagName == "H2") {
                //console.log("checking h2");
                let check = all[i].getElementsByClassName("mw-headline")
                if (check.length !== 0) {
                    //console.log(check[0].id)
                    for (let j = 0; j < idS.length; j++) {
                        if (check[0].id == idS[j]) {
                            //console.log("found see also at: " + i);
                            all[i].style.display = "none";
                            flip = true;
                        }
                    }
                }
            }
        } else {
            all[i].style.display = "none";
        }
    }

}

function stripNonArticleLinks(frame) {

    frame.querySelectorAll("a").forEach((linkEl) => {
        const href = linkEl.getAttribute("href");
        if (href && href.substring(0, 1) !== "#" && !isNormalWikipediaArticleLink(href)) {
            let newEl = document.createElement("span");
            newEl.innerHTML = linkEl.innerHTML
            linkEl.parentNode.replaceChild(newEl, linkEl)
        }
    });
}

function renderLoadFailure(frame) {
    if (!frame.innerHTML.trim()) {
        frame.innerHTML = "<p>Failed to load article.</p>";
    }
}

function isNormalWikipediaArticleLink(href) {
    return !!href &&
        href.startsWith("/wiki/") &&
        !href.startsWith("/wiki/File:") &&
        !href.startsWith("/wiki/Wikipedia:") &&
        !href.startsWith("/wiki/Category:") &&
        !href.startsWith("/wiki/Special:") &&
        !href.startsWith("/wiki/Help:") &&
        !href.startsWith("/wiki/Portal:") &&
        !href.startsWith("/wiki/Template:") &&
        !href.startsWith("/wiki/Module:") &&
        !href.startsWith("/wiki/MediaWiki:") &&
        !href.startsWith("/wiki/Template_talk:") &&
        !href.startsWith("/wiki/Portal_talk:") &&
        !href.endsWith("&redlink=1");
}
