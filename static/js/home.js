function createPromptItemHome(prompt)
{
    var link = document.createElement('a');

    link.appendChild(document.createTextNode(`#${prompt['prompt_id'].toString()}`));
    link.href="/play/" + prompt['prompt_id'];
    var startArticle = (`${prompt["start"]}`);
    
    var item = document.createElement("tr");
    
    var prompt = document.createElement("td");
    prompt.style.width = "25%";
    prompt.appendChild(document.createTextNode("Prompt "));
    prompt.append(link);
    item.appendChild(prompt);
    

    var start = document.createElement("td");
    start.style.width = "auto";
    var bolded = document.createElement("strong");
    bolded.appendChild(document.createTextNode(startArticle));

    var line = document.createElement("span");
    line.appendChild(document.createTextNode(`Starting Article: `));
    
    line.appendChild(bolded);
    start.appendChild(line);
    
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


window.addEventListener("onload", function() {
    getPromptsHome()
});