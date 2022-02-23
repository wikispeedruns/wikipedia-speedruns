function parseAndCleanPage(mainFrameEl, title) {
    
    document.getElementById("title").innerHTML = "<h1><i>"+title+"</i></h1>"

    stripNamespaceLinks(mainFrameEl)
    hideElements(mainFrameEl);
    setMargin();
}

function stripNamespaceLinks(frameBody) {

    frameBody.querySelectorAll("a").forEach((linkEl) => {
        
        if (linkEl.hasAttribute("href")) {
            if (linkEl.getAttribute("href").startsWith("/wiki/File:") || 
                linkEl.getAttribute("href").startsWith("/wiki/Wikipedia:") || 
                linkEl.getAttribute("href").startsWith("/wiki/Category:") ||
                linkEl.getAttribute("href").startsWith("/wiki/Help:")) {
                let newEl = document.createElement("span");
                newEl.innerHTML = linkEl.innerHTML
                linkEl.parentNode.replaceChild(newEl, linkEl)
            }
        }
    });

    frameBody.querySelectorAll("a").forEach(function(a) {
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

function hideElements(mainFrameEl) {
    
    const hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar", "authority-control", "external", "sistersitebox"]
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

    //hide Disambig
    
    let elements = document.getElementsByClassName("hatnote");
    for (let i=0; i < elements.length; i++) {
        let a = elements[i].getElementsByClassName("mw-disambig");
        if (a.length !== 0) {
            elements[i].style.display = "none";
        }
    }

    let all = mainFrameEl.querySelectorAll("h2, div, ul, p, h3");
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

function setMargin() {
    const element = document.getElementById("time-box");
    document.getElementById("wikipedia-frame").firstChild.style.paddingBottom = (element.offsetHeight + 25) +"px";
}

export { parseAndCleanPage };