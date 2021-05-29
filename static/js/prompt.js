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

function populateGraph(runs) {

    var graph = new Springy.Graph();

    /*
    var dennis = graph.newNode({
    label: 'Dennis',
    ondoubleclick: function() { console.log("Hello!"); }
    });
    var michael = graph.newNode({label: 'Michael'});

    graph.newEdge(dennis, michael, {color: '#00A0B0'});
    graph.newEdge(michael, dennis, {color: '#6A4A3C'});
    */
    
    var nodes = [];
    var nodeLabels = [];
    var edges = [];
    for (var i = 0; i < runs.length; i++) {
        var pathNodes = parsePath(runs[i]["path"].substring(1, runs[i]["path"].length - 1));
        for (var j = 0; j < pathNodes.length; j++) {
            if (!nodeLabels.includes(pathNodes[j])) {
                if (j === 0) {
                    nodes.push(graph.newNode({label: pathNodes[j], color: "#008000", font: "bold 18px Verdana, sans-serif", textheight: 16}));
                } else if (j === pathNodes.length - 1) {
                    nodes.push(graph.newNode({label: pathNodes[j], color: "#FF5733", font: "bold 18px Verdana, sans-serif", textheight: 16}));
                } else {
                    nodes.push(graph.newNode({label: pathNodes[j]}));
                }
                
                nodeLabels.push(pathNodes[j]);
            }
        }
        for (var j = 0; j < pathNodes.length - 1; j++) {
            let edge = {src: pathNodes[j], dest: pathNodes[j + 1], count: 1};
            if (edges.length === 0) {
                edges.push(edge);
            } else {
                var found = false;
                for (var k = 0; k < edges.length; k++) {
                    if (edge.src === edges[k].src && edge.dest === edges[k].dest) {
                        edges[k].count = edges[k].count + 1;
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    edges.push(edge);
                }
            }   
        }
    }

    var max = 0;

    for (var i = 0; i < edges.length; i++) {
        if (edges[i].count > max) {
            max = edges[i].count;
        }
    }

    for (var i = 0; i < edges.length; i++) {
        var srcIndex = nodeLabels.indexOf(edges[i].src);
        var destIndex = nodeLabels.indexOf(edges[i].dest);
        var colorScale = parseInt(255 - (255 / (max - 1)) * (edges[i].count - 1), 10);
        var weightScale = 1.5 / (max - 1) * (edges[i].count - 1) + 1.5; //map from 1.5 to 3
        graph.newEdge(nodes[srcIndex], nodes[destIndex], {color: rgbToHex(255 - colorScale, 0, colorScale), label: edges[i].count, weight: weightScale});
    }

    
    return graph;
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