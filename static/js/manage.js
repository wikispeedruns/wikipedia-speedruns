async function submitPrompt(event)
{
    event.preventDefault();

    reqBody = {};

    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("start").value}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    reqBody["start"] = body["parse"]["title"];


    const resp1 = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("end").value}`,
        {
            mode: "cors"
        }
    )
    const body1 = await resp1.json()

    reqBody["end"] = body1["parse"]["title"];

    try {
        const response = await fetch("/api/prompts/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

        console.log(response);
    } catch(e) {
        console.log(e);
    }

    getPrompts();
}

function createPromptItem(prompt)
{
    var item = document.createElement("li");
    var link = document.createElement('a');

    link.appendChild(document.createTextNode(`#${prompt['prompt_id'].toString()}`));
    link.href="/prompt/" + prompt['prompt_id'];
    
    item.appendChild(document.createTextNode(`Prompt `));
    item.append(link);
    item.append(document.createTextNode(`: ${prompt["start"]}/${prompt["end"]}`))

    var public = document.createElement('button');
    public.append(document.createTextNode(prompt["public"] ? " public" : " ranked"));

    public.onclick = (e) => {
        e.preventDefault();
        
        fetch('/api/prompts/' + prompt["prompt_id"] + "/changepublic", {
            method: "PATCH",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "public": !prompt["public"]
            })
        })

        getPrompts();
    }

    item.append(public)

    return item;
}


async function submitMarathonPrompt(event)
{
    event.preventDefault();

    reqBody = {};

    const resp = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("marathonstart").value}`,
        {
            mode: "cors"
        }
    )
    const body = await resp.json()

    reqBody["start"] = body["parse"]["title"];





    const resp1 = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("cp1").value}`,
        {
            mode: "cors"
        }
    )
    const body1 = await resp1.json()

    reqBody["cp1"] = body1["parse"]["title"];




    const resp2 = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("cp2").value}`,
        {
            mode: "cors"
        }
    )
    const body2 = await resp2.json()

    reqBody["cp2"] = body2["parse"]["title"];




    const resp3 = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("cp3").value}`,
        {
            mode: "cors"
        }
    )
    const body3 = await resp3.json()

    reqBody["cp3"] = body3["parse"]["title"];




    const resp4 = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("cp4").value}`,
        {
            mode: "cors"
        }
    )
    const body4 = await resp4.json()

    reqBody["cp4"] = body4["parse"]["title"];






    const resp5 = await fetch(
        `https://en.wikipedia.org/w/api.php?redirects=true&format=json&origin=*&action=parse&page=${document.getElementById("cp5").value}`,
        {
            mode: "cors"
        }
    )
    const body5 = await resp5.json()

    reqBody["cp5"] = body5["parse"]["title"];


    reqBody["seed"] = document.getElementById("seed").value;

    try {
        const response = await fetch("/api/prompts/marathon/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqBody)
        })

        console.log(response);
    } catch(e) {
        console.log(e);
    }

    getMarathonPrompts();
}


async function getPrompts()
{
    var list = document.getElementById("prompts");
  
    try {
        const response = await fetch("/api/prompts");
        const prompts = await response.json();

        // Remove old list
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }

        // Add new prompt
        prompts.forEach( (p) => {
            list.appendChild(createPromptItem(p));
        }); 

    } catch(e) {
        console.log(e);
    }
}



function createMarathonPromptItem(prompt)
{
    var item = document.createElement("li");
    var link = document.createElement('a');

    link.appendChild(document.createTextNode(`#${prompt['prompt_id'].toString()}`));
    link.href="/prompt/marathon/" + prompt['prompt_id'];
    
    item.appendChild(document.createTextNode(`Prompt `));
    item.append(link);
    item.append(document.createTextNode(`: ${prompt["start"]}`))
    item.append(document.createTextNode(`: ${prompt["checkpoint1"]} | ${prompt["checkpoint2"]} | ${prompt["checkpoint3"]} | ${prompt["checkpoint4"]} | ${prompt["checkpoint5"]}`))

    var public = document.createElement('button');
    public.append(document.createTextNode(prompt["public"] ? " public" : " ranked"));

    public.onclick = (e) => {
        e.preventDefault();
        
        fetch('/api/prompts/' + prompt["prompt_id"] + "/changepublic", {
            method: "PATCH",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "public": !prompt["public"]
            })
        })

        getPrompts();
    }

    item.append(public)

    return item;
}


async function getMarathonPrompts()
{
    var list = document.getElementById("marathonprompts");
  
    try {
        const response = await fetch("/api/prompts/marathon");
        const prompts = await response.json();

        // Remove old list
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }

        // Add new prompt
        prompts.forEach( (p) => {
            list.appendChild(createMarathonPromptItem(p));
        }); 

    } catch(e) {
        console.log(e);
    }
}





window.addEventListener("load", function() {
    document.getElementById("newPrompt").addEventListener("submit", submitPrompt);
    getPrompts()
});


window.addEventListener("load", function() {
    document.getElementById("newMarathonPrompt").addEventListener("submit", submitMarathonPrompt);
    getMarathonPrompts()
});