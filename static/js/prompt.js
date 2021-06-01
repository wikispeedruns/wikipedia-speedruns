function generate_prompt(prompt)
{
    document.getElementById("prompt").innerHTML = prompt["start"] + "/" + prompt["end"];
}

function generate_leaderboard(runs)
{
    var table = document.getElementById("leaderboard");
    // TODO probably add class and stuff
    for (var i = 0; i < runs.length; i++) {

        var item = document.createElement("tr");
        
        var rank = document.createElement("td");
        rank.appendChild(document.createTextNode(i + 1));

        var time = document.createElement("td");
        time.appendChild(document.createTextNode((runs[i]["run_time"]/1000000).toFixed(2) + " s"));

        var path = document.createElement("td");
        path.appendChild(document.createTextNode(runs[i]["path"]));

        var name = document.createElement("td");
        name.appendChild(document.createTextNode(runs[i]["name"]));

        if (runs[i]["run_id"] === Number(run_id)) {
            item.style.fontWeight = "bold";
        }

        item.appendChild(rank);
        item.appendChild(name);
        item.appendChild(time);
        item.appendChild(path);
        

        table.appendChild(item);
    }
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function parsePath(path) {
    var nodes = path.split("\', \'");
    var out = [];
    
    for (var i = 0; i < nodes.length; i++) {
        if (i === 0) {
            out.push(nodes[i].substring(1, nodes[i].length));
        } else if  (i === nodes.length - 1) {
            out.push(nodes[i].substring(0, nodes[i].length - 1));
        } else {
            out.push(nodes[i]);
        }
    }
    
    return out;
}

window.onload = async function() {

    var response = await fetch("/api/prompts/get/" + prompt_id);
    const prompt = await response.json();

    response = await fetch("/api/prompts/get/" + prompt_id + "/runs");
    const runs = await response.json(); 

    generate_prompt(prompt);
    generate_leaderboard(runs);
    var graph1 = populateGraph(runs);
    $('#springydemo').springy({ graph: graph1 });
}