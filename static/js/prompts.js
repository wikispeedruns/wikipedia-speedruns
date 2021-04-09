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
        prompts.forEach( (el) => {
            const item = document.createElement("li");
            item.appendChild(document.createTextNode(`Prompt #${el["prompt_id"]}: ${el["start"]} -> ${el["end"]}`));
            list.appendChild(item);
        }); 

    } catch(e) {
        console.log(e);
    }
}


window.onload = function() {
    document.getElementById("newPrompt").addEventListener("submit", submitPrompt);
    getPrompts()
}