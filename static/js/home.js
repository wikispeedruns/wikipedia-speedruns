function createPromptItemHome(prompt)
{
    var link = document.createElement('a');

    link.appendChild(document.createTextNode(`#${prompt['prompt_id'].toString()}`));
    link.href="/play/" + prompt['prompt_id'];
    var startArticle = (`${prompt["start"]}`);
    var item = document.createElement("tr");
    
    var prompt = document.createElement("td");
    var start = document.createElement("td");
    prompt.style.width = "25%";
    start.style.width = "auto";
    prompt.appendChild(document.createTextNode("Prompt "));
    prompt.append(link);
    start.appendChild(document.createTextNode(`Starting Article: ` + startArticle));
    item.appendChild(prompt);
    item.appendChild(start);

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

        var item = document.createElement("tr");
        var header1 = document.createElement("th");
        var header2 = document.createElement("th");
        header1.style.width = "25%";
        header1.style.width = "auto";
        header1.appendChild(document.createTextNode("Prompt #"));
        header2.appendChild(document.createTextNode("Starting Article"));
        item.appendChild(header1);
        item.appendChild(header2);
        list.appendChild(item);

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