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
    var publicList = document.getElementById("publicPrompts");
    var ratedList = document.getElementById("ratedPrompts");

    try {
        queryString = "";
       
        // Defined in base.html based on template
        if (!user_id) {
            queryString = "?public=true"
        }

        const response = await fetch("/api/prompts" + queryString);

        const prompts = await response.json();

        // Remove old list(s)
        while (publicList.firstChild) {
            publicList.removeChild(publicList.firstChild);
        }
        while (ratedList.firstChild) {
            ratedList.removeChild(ratedList.firstChild);
        }

        var item = document.createElement("tr");
        var header1 = document.createElement("th");
        var header2 = document.createElement("th");
        //header1.style.width = "50%";
        header1.style.width = "auto";
        header1.style.paddingRight = "40px";
        header1.appendChild(document.createTextNode("Prompt #"));
        header2.appendChild(document.createTextNode("Starting Article"));
        item.appendChild(header1);
        item.appendChild(header2);

        publicList.appendChild(item);
        ratedList.appendChild(item.cloneNode(true))
        
        if (!user_id) {
            ratedList.style="display: none"
        }

        // Add new prompt
        prompts.forEach( (p) => {
            if (p["public"])
                publicList.appendChild(createPromptItemHome(p));
            else
                ratedList.appendChild(createPromptItemHome(p));
        }); 

    } catch(e) {
        console.log(e);
    }
}


window.addEventListener("load", function() {
    getPromptsHome()
});