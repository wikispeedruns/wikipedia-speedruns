function createPromptItemHome(prompt)
{
    var item = document.createElement("li");
    var link = document.createElement('a');

    link.appendChild(document.createTextNode(`#${prompt['prompt_id'].toString()}`));
    link.href="/play/" + prompt['prompt_id'];
    
    item.appendChild(document.createTextNode(`Prompt `));
    item.append(link);
    item.append(document.createTextNode(`Starting Article: ${prompt["start"]}`))

    return item;
}


async function getPromptsHome()
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
            list.appendChild(createPromptItemHome(p));
        }); 

    } catch(e) {
        console.log(e);
    }
}


window.onload = function() {
    getPromptsHome()
}