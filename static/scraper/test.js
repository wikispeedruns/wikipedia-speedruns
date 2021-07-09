var startPage = "";
var goalPage = "";
var path = [];
var pathLength = 0;

async function submitPrompt(event)
{
    event.preventDefault();

    startPage = await getTitle(document.getElementById("start").value);
    goalPage = await getTitle(document.getElementById("end").value);
    //console.log(startPage + " , " + goalPage);

    var startTime = Date.now();

    var titles = await getTitles(startPage);

    var endTime = Date.now();

    console.log((endTime - startTime) + "ms");

    //var displayBlock = document.getElementById("testDisp");
    
    //for (let index = 0; index < titles.length; index++) {
    //    var a = document.createElement("p");
    //    a.appendChild(document.createTextNode(titles[index]));
    //    displayBlock.appendChild(a);
    //}


    //var found = await crawler();

    /*
    if (!found) {
        var endTime = Date.now();
        document.getElementById("output").innerHTML = "Did not find path for: " + startPage + ", " + goalPage + " in under 15 pages\n" + startTime + " , " + endTime;
    } else {
        //console.log(path);
        var endTime = Date.now();
        //document.getElementById("output").innerHTML = formatPathObj(path.length - 1 + ": " + path + "\n" + startTime + " , " + endTime)
        document.getElementById("output").innerHTML = pathLength;
    }
    */
}

async function crawler() {
    var queue = [];
    

    queue.push({title:startPage, dist:0 , pred:"", id: 0});
    //var visited = [];
    //visited[bodyArr[1]] = {title:bodyArr[0], dist:0 , pred:"", id: bodyArr[1]};
    //counter = 0;

    while (queue.length > 0) {
        //counter++;
        //console.log(counter);
        
        var node = queue.shift();

        var links = await getLinks(node.title);
         
        if (links[0] == goalPage) {
            pathLength = node.dist;
            //getPath(visited);
            return true;
        }

        for (var i = 2; i < links.length; i++) {
            //if (!visited[node.id].title) {
            //    visited.push({title:links[i], dist:(node.dist + 1), pred:links[0], id = 0});
            queue.push({title:links[i], dist:(node.dist + 1), pred:links[0], id:0});
            //}
        }
        
    }
    return false;
}

function getPath(visited) {
    //TODO fix
    console.log(visited);
    path = [];
    var crawl = visited[findLink(visited, goalPage)];
    path.push(crawl);
    while (crawl.title !== startPage) {
        crawl = visited[findLink(visited, crawl.pred)];
        path.push(crawl);
    }
}

function findLink(visited, link) {
    for (var i = 0; i < visited.length; i++) {
        if (visited[i].title === link) {
            return i;
        }
    }
    return -1;
}

async function getTitles(page) {
    var links = await getLinks(page);
    console.log(links.length + " links");


    
    let titleBuffer = [];
    let titles = [];

    let batchSize = 100;
    let loaded = 2;

    while (loaded < links.length) {

        var startTime = Date.now();
        for (let j = 0; j < batchSize && loaded < links.length; j++) {
            titleBuffer.push(getTitle(links[loaded]))
            loaded++
        }

        await Promise.all(titleBuffer).then(temp => {
            titles.push(...temp)
        })

        var endTime = Date.now();

        console.log(endTime - startTime);

        titleBuffer.splice(0, titleBuffer.length)
    }


    /*
    while (loaded < links.length) {
        var target = (loaded + batchSize < links.length) ? loaded + batchSize : links.length;

        while (loaded < target) {
            titles.push(await getTitle(links[loaded]));
            loaded++;
        }
        Promise.all(titles).then(results => {
            results.forEach(element => {
            var a = document.createElement("p");
            a.appendChild(document.createTextNode(element));
            displayBlock.appendChild(a);
            });
            console.log("loaded until " + loaded);
        });
    }

    Promise.all(titles).then({});
    */

    
    renderTitles(titles);
    console.log(titles);
    return titles;
    
}


function renderTitles(arr) {
    var displayBlock = document.getElementById("testDisp");
    arr.forEach(element => {
        var a = document.createElement("p");
        a.appendChild(document.createTextNode(element));
        displayBlock.appendChild(a);
    });
}

async function getLinks(page) {
    console.log("getting links for: " + page);
    //var pre = Date.now();
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json();
    //var start = Date.now();
    var links = [];
    links.push(body["parse"]["title"]);
    links.push(body["parse"]["pageid"]);
    
    if (body["parse"]["title"] === goalPage) {
        return links;
    }

    document.getElementById("wikipedia-frame").innerHTML = body["parse"]["text"]["*"];
    hideElements();

    var elements = [];
    var loop = true;

    elements.push(document.querySelectorAll("#wikipedia-frame").item(0));
    
    while (loop) {
        loop = false;
        var len = elements.length;
        for (var i = 0; i < len; i++) {
            var cur = elements.shift();
            var childNodes = cur.childNodes;
            if (cur.tagName === "A") {
                var link = handleWikipediaLink(cur);
                if (link !== null) {
                    //console.log(link);
                    links.push(link);
                }
            }
            if (childNodes.length > 0) {
                loop = true;
                childNodes.forEach(el => {
                    if (checkNode(el)) {
                        elements.push(el);
                    }
                })
            }
        }
    }
    //console.log(Date.now() - start)
    //console.log(Date.now() - pre)
    //console.log("links for " + page + ": " + links.length);
    return links;
}

function handleWikipediaLink(el) 
{

    linkURL = el.getAttribute("href");

    if (linkURL === null) return null;
    // ignore target scrolls
    if (linkURL.substring(0, 1) === "#") return null;
    // Ignore external links
    if (linkURL.substring(0, 6) !== "/wiki/") return null;

    if (linkURL.substring(0, 11) === "/wiki/File:") return null;
    //if (linkURL.substring())

    return linkURL.substring(6);
}


async function getTitle(page) {

    /*
    //var start = Date.now();
    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&prop=&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()
    //console.log(body);
    //console.log(Date.now() - start)
    return await body["parse"]["title"]
    */

    return new Promise((resolve, reject) => {
        fetch(`https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&prop=&page=${page}`)
            .then((resp) => resp.json())
            .then((body) => {
                resolve(body["parse"]["title"])
            })
    })
}

function checkNode(el) {
    
    //console.log(el);
    if (el.tagName) {
        if (el.style.display === "none") {
            return false;
        }
    } 
    
    var hideEntire = ['mw-disambig']
    for(i=0; i<hideEntire.length; i++) {
        if (el.className) {
            if (el.className === hideEntire[i]) {
                return false;
            }
        }
    }
    
    var idS = ["lmaotestID"];
    for(i=0; i<idS.length; i++) {
        if (el.id === idS[i]) {
            return false;
        }
    }

    return true;
    
}

function hideElements() {
    
    var hide = ["reference","mw-editsection","reflist","portal","refbegin", "sidebar", "authority-control", "external", "sistersitebox", "mw-disambig"]
    for(i=0; i<hide.length; i++) {
        var elements = document.getElementsByClassName(hide[i]);
        //console.log("found: " + hide[i] + elements.length)
        for(j=0; j<elements.length; j++) {
            elements[j].style.display = "none";
        }
    }
    
    var idS = ["See_also", "Notes_and_references", "Further_reading", "External_links", "References", "Notes", "Citations", "Explanatory_notes"];
    for(i=0; i<idS.length; i++) {
        var e = document.getElementById(idS[i]);
        if (e !== null) {
            e.style.display = "none";
        }
    }

    //hide Disambig
    
    var elements = document.getElementsByClassName("hatnote");
    for (i=0; i < elements.length; i++) {
        var a = elements[i].getElementsByClassName("mw-disambig");
        //console.log(a)
        if (a.length !== 0) {
            elements[i].style.display = "none";
        }
        //mw-disambig
    }

    //var all = document.getElementsByClassName("mw-parser-output")[0].querySelectorAll("h2", "div", "ul", "p");
    var all = document.getElementById("wikipedia-frame").querySelectorAll("h2, div, ul, p, h3");
    var flip = false
    for (i = 0; i < all.length; i++) {
        if (!flip) {
            if (all[i].tagName == "H2") {
                //console.log("checking h2");
                var check = all[i].getElementsByClassName("mw-headline")
                if (check.length !== 0) {
                    //console.log(check[0].id)
                    for (j = 0; j < idS.length; j++) {
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

function formatPathObj(pathArr) {
    output = "";
    for(i=0; i<pathArr.length - 1;i++) {
        output = output.concat(pathArr[i].title)
        output = output.concat(",")
    }
    output = output.concat(pathArr[pathArr.length - 1].title)
    return output;
}

window.onload = async function() {
    document.getElementById("newPrompt").addEventListener("submit", submitPrompt);
    
}