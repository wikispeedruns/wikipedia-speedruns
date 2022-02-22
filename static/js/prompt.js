import { serverData } from "./modules/serverData.js"

const prompt_id = serverData["prompt_id"];
const run_id = serverData["run_id"] || "";
const pg = serverData["pg"];

const runsPerPage = 10;

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
    var edges = [];

    var checkIncludeLabels = function(label, array) {
        for (let i = 0; i < array.length; i++) {
            if (array[i].label === label) {
                return i;
            }
        }
        return -1;
    }

    var checkIncludeEdgeLabels = function(src, dest, array) {
        for (let i = 0; i < array.length; i++) {
            if (array[i].src === src && array[i].dest === dest) {
                return i;
            }
        }
        return -1;
    }

    var startNode;
    var endNode;
    

    for (let i = 0; i < runs.length; i++) {
        if (!runs[i]["user_id"] && runs[i]["run_id"] !== Number(run_id)) continue;

        var pathNodes = runs[i]["path"]
        var cur = (runs[i]["run_id"] === Number(run_id)) ? true : false;

        for (let j = 0; j < pathNodes.length; j++) {
            var index = checkIncludeLabels(pathNodes[j], nodes);
            if (index === -1) {
                let node = {type: 0, label: pathNodes[j], count: 1, current: cur};
                if (j === 0) {
                    node.type = 1;
                    startNode = node;
                } 
                else if (j === pathNodes.length - 1) {
                    node.type = 2;
                    endNode = node;
                } 
                else {
                    node.type = 0;
                    nodes.push(node);
                }
                
                //let node = {type: type, label: pathNodes[j], count: 1, current: cur};
                //nodes.push(node);
                
            } else {
                if (cur) {
                    nodes[index].current = cur;
                }
                nodes[index].count = nodes[index].count + 1;
            }
        }
    }

    if (runs.length > 0) {
        nodes.push(startNode);
        nodes.push(endNode);
    }


    for (let i = 0; i < runs.length; i++) {
        if (!runs[i]["user_id"] && runs[i]["run_id"] !== Number(run_id)) continue;


        var pathNodes = runs[i]["path"]
        var cur = (runs[i]["run_id"] === Number(run_id)) ? true : false;

        for (let j = 0; j < pathNodes.length - 1; j++) {


            let index = checkIncludeEdgeLabels(pathNodes[j], pathNodes[j + 1], edges);

            if (index === -1) {
                let edge = {src: pathNodes[j], dest: pathNodes[j + 1], count: 1, current: cur};
                edges.push(edge);
            } else {
                if (cur) {
                    edges[index].current = cur;
                }
                edges[index].count = edges[index].count + 1;
            }
        }
    }

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

    })

    edges.forEach(function(edge) {
        if (edge.count > edgeCountMax) {
            edgeCountMax = edge.count;
        }
    })

    edges.forEach(function(edge) {
        var srcIndex = nodeLabels.indexOf(edge.src);
        var destIndex = nodeLabels.indexOf(edge.dest);
        var colorScale;
        var weightScale;

        if (edgeCountMax === 1) {
            colorScale = 255;
            weightScale = 2.25;
        } else {
            colorScale = parseInt(255 - (255 / (edgeCountMax - 1)) * (edge.count - 1), 10);
            weightScale = 1.5 / (edgeCountMax - 1) * (edge.count - 1) + 1.5; //map from 1.5 to 3
        }

        var color = edge.current ? "#ff9700" : rgbToHex(255 - colorScale, 0, colorScale);
        graph.newEdge(nodeObj[srcIndex], nodeObj[destIndex], {color: color, label: edge.count, weight: weightScale});


    })

    
    return graph;
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        prompt: [],
        runs: [],
        renderedRuns: [],
        renderedRunsRank: [],
        currentRun: null,
        currentRunPosition: 0,
        currentRunRank: 0,
        runsPerPage: runsPerPage
    },

    methods : {
        getLeaderboard: async function () {

            var response = await fetch("/api/sprints/" + prompt_id + "/leaderboard/" + run_id);

            if (response.status == 401) {
                alert(await response.text());
                window.location.replace("/");   // TODO error page
            }


            return await response.json(); 
        }, 

        genGraph: function () {
            var paths = this.renderedRuns;
            if (this.currentRunPosition === -1 || this.currentRunPosition === 1) {
                paths = paths.concat(this.currentRun)
            }
            var graph1 = populateGraph(paths);
            $('#springydemo').springy({ graph: graph1 });
        },

        getPageNo: function () {
            if (this.runs.length === 0) {
                return 0;
            }
            return parseInt(pg)
        },

        getPromptID: function() {
            return prompt_id;
        },

        getRunID: function() {
            return run_id;
        },

        paginate: function () {
            const first = (pg-1) * runsPerPage
            const last = pg * runsPerPage
            for (let i = 0; i < this.runs.length; i++) {
                let run = this.runs[i]
                if (run_id) {
                    if (run.run_id === parseInt(run_id)) {
                        this.currentRun = run;
                        this.currentRunRank = i+1;
                        if (i < first) {
                            this.currentRunPosition = -1;
                        } else if (i >= last) {
                            this.currentRunPosition = 1;
                        }
                    }
                }

                if (i >= first && i < last) {
                    this.renderedRuns.push(run)
                    this.renderedRunsRank.push(i+1)
                }

            }
        },

        getRenderedRank: function (index) {
            return this.renderedRunsRank[index];
        },

        nextPage: function () {
            //TODO: look into ways to use JS methods to update/insert new args
            if (run_id) {
                window.location.replace("/prompt/" + prompt_id + "?page=" + String(parseInt(pg)+1) + "&run_id=" + run_id);
            } else {
                window.location.replace("/prompt/" + prompt_id + "?page=" + String(parseInt(pg)+1));
            }
        }, 

        prevPage: function() {
            if (run_id) {
                window.location.replace("/prompt/" + prompt_id + "?page=" + String(parseInt(pg)-1) + "&run_id=" + run_id);
            } else {
                window.location.replace("/prompt/" + prompt_id + "?page=" + String(parseInt(pg)-1));
            }
        }
    },

    created: async function() {
        const resp = await this.getLeaderboard();

        this.prompt = resp["prompt"];
        this.runs = resp["leaderboard"];

        this.paginate();      
        this.genGraph();
    }
})