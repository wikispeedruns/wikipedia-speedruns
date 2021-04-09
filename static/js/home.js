async function submitPrompt(event)
{
    event.preventDefault();

    reqBody = {}
    reqBody["start"] = document.getElementById("start").value;
    reqBody["end"] = document.getElementById("end").value;

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