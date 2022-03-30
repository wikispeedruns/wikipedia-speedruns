import { getArticle } from "../wikipediaAPI/util.js";

export class ArticleRenderer {

    /* frame: DOM element (i.e. through getElementById) to render article in
     * pageCallback: Called upon loading an article, should expect new page and load time
     */
    constructor(frame, pageCallback, mouseEnter, mouseLeave) {
        this.frame = frame;
        this.pageCallback = pageCallback;
        this.mouseEnter = mouseEnter;
        this.mouseLeave = mouseLeave;
    }

    async loadPage(page) {
        try {
            const startTime = Date.now();
            const body = await getArticle(page);

            this.frame.innerHTML = body["text"]["*"];

            // Create title
            let titleEl = document.createElement("div");
            titleEl.innerHTML = "<h1><i>" + body["title"] + "</i></h1>";
            this.frame.insertBefore(titleEl, this.frame.firstChild);


            hideElements(this.frame);
            // disableFindableLinks(this.frame);
            stripNamespaceLinks(this.frame);


            this.frame.querySelectorAll("a, area").forEach((el) => {
                // Arrow function to prevent this from being overwritten
                el.onclick = (e) => this.handleWikipediaLink(e);
                if (window.screen.width >= 768 && el.hasAttribute("href") && el.getAttribute("href").startsWith("/wiki/")) {
                    el.onmouseenter = this.mouseEnter;
                    el.onmouseleave = this.mouseLeave;
                }
            });

            window.scrollTo(0, 0);

            this.pageCallback(body["title"], Date.now() - startTime);

        } catch (error) {

            console.log(error)
            // Reenable all links if loadPage fails
            this.frame.querySelectorAll("a, area").forEach((el) => {
                // Arrow function to prevent this from being overwritten
                el.onclick = (e) => this.handleWikipediaLink(e);
            });
        }
    }


    handleWikipediaLink(e) {
        e.preventDefault();

        const linkEl = e.currentTarget;

        if (linkEl.getAttribute("href").substring(0, 1) === "#") {
            let a = linkEl.getAttribute("href").substring(1);
            document.getElementById(a).scrollIntoView();

        } else {
            // Ignore external links and internal file links
            // TODO merge this with stripNamespaceLinks
            if (!linkEl.getAttribute("href").startsWith("/wiki/") || linkEl.getAttribute("href").startsWith("/wiki/File:")) {
                return;
            }

            // Disable the other linksto prevent multiple clicks
            this.frame.querySelectorAll("a, area").forEach((el) =>{
                el.onclick = (e) => {
                    e.preventDefault();
                    console.log("prevent multiple click");
                };
            });

            // Remove "/wiki/" from string
            this.loadPage(linkEl.getAttribute("href").substring(6))
        }
    }
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

    // hide Disambig

    let elements = document.getElementsByClassName("hatnote");
    for (let i=0; i < elements.length; i++) {
        let a = elements[i].getElementsByClassName("mw-disambig");
        if (a.length !== 0) {
            elements[i].style.display = "none";
        }
    }

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

function stripNamespaceLinks(frame) {

    frame.querySelectorAll("a").forEach((linkEl) => {

        if (linkEl.hasAttribute("href")) {
            if (linkEl.getAttribute("href").startsWith("/wiki/File:") ||
                linkEl.getAttribute("href").startsWith("/wiki/Wikipedia:") ||
                linkEl.getAttribute("href").startsWith("/wiki/Category:") ||
                linkEl.getAttribute("href").startsWith("/wiki/Help:") ||
                linkEl.getAttribute("href").endsWith("&redlink=1")) {
                let newEl = document.createElement("span");
                newEl.innerHTML = linkEl.innerHTML
                linkEl.parentNode.replaceChild(newEl, linkEl)
            }
        }
    });
}

function disableFindableLinks(frame) {

    // Disable CTRL + F by splitting up link text into different div
    frame.querySelectorAll("a").forEach(function(a) {
        let iter = document.createNodeIterator(a, NodeFilter.SHOW_TEXT);
        let textNode;

        while (textNode = iter.nextNode()) {
            let replacementNode = document.createElement('div');
            replacementNode.innerHTML = '<div style="display:inline-block">' + textNode.textContent.split('').map(function(character) {
                return '<div style="display:inline-block">' + character.replace(/\s/g, '&nbsp;') + '</div>'
            }).join('') + '</div>'
            textNode.parentNode.insertBefore(replacementNode.firstChild, textNode);
            textNode.parentNode.removeChild(textNode);
        }
    });
}
