function generate_prompt(prompt)
{
    document.getElementById("prompt").innerHTML = prompt["start"] + "/" + prompt["end"];
}

function generate_leaderboard(runs)
{
    var table = document.getElementById("leaderboard");
    for (var i = 0; i < runs.length; i++) {
        var item = document.createElement("tr");
        
        var time = document.createElement("td");
        time.appendChild(document.createTextNode(runs[i]["run_time"]/100000 + " s"));

        var path = document.createElement("td");
        path.appendChild(document.createTextNode(runs[i]["path"]));

        item.appendChild(time);
        item.appendChild(path);

        table.appendChild(item);
    }
}


window.onload = async function() {
    var response = await fetch("/api/prompts/get/" + prompt_id);
    const prompt = await response.json();

    response = await fetch("/api/prompts/get/" + prompt_id + "/runs");
    const runs = await response.json(); 

    generate_prompt(prompt);
    generate_leaderboard(runs);
}