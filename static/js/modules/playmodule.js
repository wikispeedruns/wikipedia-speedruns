import { parseAndCleanPage } from "./wikipediapageparse.js"

let vueContainer = null;
let timerInterval = null;

async function playGame(app) {

    //get the vue object passed from play.js. It will contain prompt and run information
    vueContainer = app;
    //start the countdown, and preload the starting article
    await Promise.all([countdown(), loadPage(vueContainer.$data.startArticle)]);

    //once above conditions are met, toggle the `started` render flag, which will hide all other elements, and display the rendered wikipage
    vueContainer.$data.started = true;
    //start timer
    vueContainer.$data.startTime = Date.now();

    //set the timer update interval
    timerInterval = setInterval(function() {
        const seconds = (Date.now() - vueContainer.$data.startTime) / 1000;
        vueContainer.$data.timer = seconds;
    }, 50);

}

//Load a page given its article title
async function loadPage(page) {

    const resp = await fetch( //Note: wikipedia will also process any redirects in this API call, so the response will always be a valid page
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${page}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()
    const title = body["parse"]["title"]

    //load our main wikipedia page DOM element with the body of the API response
    let frameBody = document.getElementById("wikipedia-frame")
    frameBody.innerHTML = body["parse"]["text"]["*"]

    //process the next step in game logic, given that we reached a new page. This function should be dependent on gamemode.
    await processGameLogic(title);
    
    /*clean up page's links and formatting, including:
        hide elements on the wikipedia page that players should not use
        strip hyperlinks that lead to wikipedia namespaced pages
        setting the bottom padding of the main element (prevents the HUD from blocking text at the bottom)
    */
    parseAndCleanPage(frameBody, title);

    //Set the click event of all links on page
    document.querySelectorAll("#wikipedia-frame a, #wikipedia-frame area").forEach((el) =>{
        el.onclick = handleWikipediaLink;
    });

    //After rendering is complete, scroll to top of page
    window.scrollTo(0, 0)
}



async function processGameLogic(title) {

    //add newest page visited to the array storing path
    vueContainer.$data.path.push(title);

    //Game logic for sprint mode:
        //if the page's title matches that of the end article, finish the game, and submit the run
    if (vueContainer.$data.gameType === "sprint") {
    
        if (title.replace("_", " ").toLowerCase() === vueContainer.$data.endArticle.replace("_", " ").toLowerCase()) {
            await genericFinish();
            await submitSprint();
        }

    }
}


//click event handling for each link
function handleWikipediaLink(e) 
{
    e.preventDefault();

    const linkEl = e.currentTarget;

    if (linkEl.getAttribute("href").substring(0, 1) === "#") {
        let a = linkEl.getAttribute("href").substring(1);
        //console.log(a);
        document.getElementById(a).scrollIntoView();

    } else {

        // Ignore external links and internal file links
        if (!linkEl.getAttribute("href").startsWith("/wiki/") || linkEl.getAttribute("href").startsWith("/wiki/File:")) {
            return;
        }

        // Disable the other linksto prevent multiple clicks
        document.querySelectorAll("#wikipedia-frame a, #wikipedia-frame area").forEach((el) =>{
            el.onclick = (e) => {
                e.preventDefault();
                console.log("prevent multiple click");
            };
        });

        // Remove "/wiki/" from string
        loadPageWrapper(linkEl.getAttribute("href").substring(6))
    }
}

async function loadPageWrapper(page) {
    try {
        await loadPage(page)
    } catch (error) {
        // Reenable all links if loadPage fails
        document.querySelectorAll("#wikipedia-frame a, #wikipedia-frame area").forEach((el) =>{
            el.onclick = handleWikipediaLink;
        });
    }
}

async function genericFinish() {
    //toggle the finished render flag. This will hide the main page block and show the finishing stats
    vueContainer.$data.finished = true;
    vueContainer.$data.finalTime = vueContainer.$data.timer;
    // Stop timer
    clearInterval(timerInterval);
    vueContainer.$data.endTime = vueContainer.$data.startTime + vueContainer.$data.finalTime*1000;
    // Prevent are you sure you want to leave prompt
    window.onbeforeunload = null;
}


//Submit run information to endpoint as an update of the previously generated empty run 
async function submitSprint() {

    const reqBody = {
        "start_time": vueContainer.$data.startTime,
        "end_time": vueContainer.$data.endTime,
        "path": vueContainer.$data.path,
    }

    // Send results to API
    try {
        const response = await fetch(`/api/runs/${vueContainer.$data.run_id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

    } catch(e) {
        console.log(e);
    }
}

// Race condition between countdown timer and "immediate start" button click
// Resolves when either condition resolves
async function countdown() {

    let countDownStart = Date.now();
    let countDownTime = vueContainer.$data.countdown * 1000;

    document.getElementById("mirroredimgblock").classList.toggle("invisible");

    // Condition 1: countdown timer
    const promise1 = new Promise(resolve => {
        const x = setInterval(function() {
            const now = Date.now()
          
            // Find the distance between now and the count down date
            let distance = countDownStart + countDownTime - now;
            vueContainer.$data.countdown = Math.floor(distance/1000)+1;

            if (distance <= -500) { //Allow timer to reach 0
                resolve();
                clearInterval(x);
            }

            if (distance < 700 && distance > 610 && document.getElementById("mirroredimgblock").classList.contains("invisible")) {                
                document.getElementById("mirroredimgblock").classList.toggle("invisible")
            }

        }, 50);
    });

    // Condition 2: "immediate start" button click
    const promise2 = new Promise(r =>
        document.getElementById("start-btn").addEventListener("click", r, {once: true})
    )

    await Promise.any([promise1, promise2]);
}

export {playGame};