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
        const response = await fetch("/api/prompts/create", {
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

    return item;
}

async function getPrompts()
{
    var list = document.getElementById("prompts");
  
    try {
        const response = await fetch("/api/prompts/get");
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


window.onload = function() {
    document.getElementById("newPrompt").addEventListener("submit", submitPrompt);
    getPrompts()
}