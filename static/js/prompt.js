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
    */
    
    var nodes = [];
    var nodeLabels = [];
    var edges = [];
    for (var i = 0; i < runs.length; i++) {
        var pathNodes = parsePath(runs[i]["path"].substring(1, runs[i]["path"].length - 1));
        for (var j = 0; j < pathNodes.length; j++) {
            if (!nodeLabels.includes(pathNodes[j])) {
                var color;
                var font;
                var textheight;
                var type;
                if (j === 0) {
                    color = "#008000";
                    font= "bold 15px Verdana, sans-serif";
                    textheight = 18;
                    type = 1;
                } else if (j === pathNodes.length - 1) {
                    color = "#FF5733";
                    font= "bold 15px Verdana, sans-serif";
                    textheight = 18;
                    type = 2;
                } else {
            
                    color = (runs[i]["run_id"] === Number(run_id)) ? "#ff9700" : "#000000";
                    font= "10px Verdana, sans-serif";
                    textheight = 10;
                    type = 0;
                }

                nodes.push(graph.newNode({label: pathNodes[j], color: color, font: font, textheight: textheight, type: type}));
                nodeLabels.push(pathNodes[j]);
            }
        }

        
        for (var j = 0; j < pathNodes.length - 1; j++) {

            var curId = (runs[i]["run_id"] === Number(run_id)) ? true : false;


            let edge = {src: pathNodes[j], dest: pathNodes[j + 1], count: 1, highlight: curId};
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

<<<<<<< Updated upstream
    var max = 0;
=======
    var edgeCountMax = 0;
    var nodeCountMax = 0;
    var nodeObj = [];
    var nodeLabels = [];

    nodes.forEach(function(node) {
        if (node.count > nodeCountMax) {
            nodeCountMax = node.count;
        }
    })
    nodes.forEach(function(node) {
        var color;
        var font;
        var textheight;

        if (node.type === 1) {
            color = "#008000";
            font= "bold 15px Verdana, sans-serif";
            textheight = 18;
        } else if (node.type === 2) {
            color = "#FF5733";
            font= "bold 15px Verdana, sans-serif";
            textheight = 18;
        } else {
            color = "#000000";
            font= "10px Verdana, sans-serif";
            textheight = 10;
        }

        var color = (node.current && node.type !== 1 && node.type !== 2) ? "#ff9700" : color;

        var weightScale;
        if (nodeCountMax === 1) {
            weightScale = 12;
        } else {
            weightScale = 12 / (nodeCountMax - 1) * (node.count - 1) + 6; //map from 6 to 18
        }

        var n = graph.newNode({label: node.label, color: color, font: font, textheight: textheight, type: node.type, weightScale: weightScale, count: node.count});
        nodeObj.push(n);
        nodeLabels.push(node.label);
>>>>>>> Stashed changes

    for (var i = 0; i < edges.length; i++) {
        if (edges[i].count > max) {
            max = edges[i].count;
        }
    }

    for (var i = 0; i < edges.length; i++) {
        var srcIndex = nodeLabels.indexOf(edges[i].src);
        var destIndex = nodeLabels.indexOf(edges[i].dest);
        var colorScale;
        var weightScale;
        if (max === 1) {
            colorScale = 255;
            weightScale = 2.25;
        } else {
            colorScale = parseInt(255 - (255 / (max - 1)) * (edges[i].count - 1), 10);
            weightScale = 1.5 / (max - 1) * (edges[i].count - 1) + 1.5; //map from 1.5 to 3
        }
        //console.log(edges[i].src);
        //console.log(nodes[srcIndex]);
        //console.log(nodes[destIndex]);
        var color = edges[i].highlight ? "#ff9700" : rgbToHex(255 - colorScale, 0, colorScale);

        graph.newEdge(nodes[srcIndex], nodes[destIndex], {color: color, label: edges[i].count, weight: weightScale});
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