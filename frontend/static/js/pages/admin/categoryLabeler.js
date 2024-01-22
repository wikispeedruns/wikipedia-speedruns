import Vue from "vue/dist/vue.esm.js";

async function getRandomArticles() {
    const url =
    "https://en.wikipedia.org/w/api.php?action=query&origin=*&format=json&list=random&rnlimit=15";
    const resp = await fetch(url, { mode: "cors" });
    const body = await resp.json();
    return body["query"]["random"];
}

async function getArticlesUnderCategory(categoryTitle) {
    let output = [];
    let categoryNames = [];

    let url = `https://en.wikipedia.org/w/api.php?action=query&origin=*&format=json&list=categorymembers&cmtitle=${categoryTitle}&cmtype=subcat`;
    const resp = await fetch(url, { mode: "cors" });
    const body = await resp.json();
    const subcats = body["query"]["categorymembers"];
    subcats.forEach((sc) => categoryNames.push(sc["title"]));
    categoryNames.push(categoryTitle);

    categoryNames.forEach(async function (sc) {
    url = `https://en.wikipedia.org/w/api.php?action=query&origin=*&format=json&list=categorymembers&cmtitle=${sc}`;
    const scresp = await fetch(url, { mode: "cors" });
    const scbody = await scresp.json();
    scbody["query"]["categorymembers"].forEach(function (m) {
        if (m["ns"] == 0) output.push(m);
    });
    });

    return { subcats: categoryNames, articles: output };
}

var app = new Vue({
    delimiters: ["[[", "]]"],
    el: "#app",

    data: {
    categories: [
        { disp: "Natural Sciences", id: "NSCI" },
        { disp: "Geography", id: "GEOG" },
        { disp: "Ecology", id: "ECOL" },
        { disp: "Technology", id: "TECH" },
        { disp: "Human Health & Medicine", id: "HLTH" },
        { disp: "Human Society", id: "SSCI" },
        { disp: "People", id: "PPLE" },
        { disp: "Government & Politics", id: "GOVM" },
        { disp: "Economy & Business", id: "ECMY" },
        { disp: "Consumer goods", id: "CSMR" },
        { disp: "The Arts", id: "CULT" },
        { disp: "Human History", id: "HIST" },
        { disp: "Religion", id: "RELG" },
        { disp: "Food & Drinks", id: "FOOD" },
        { disp: "Sports & Games", id: "SPRT" },
        { disp: "Entertainment", id: "ENTR" },
    ],
    categoryName: "",
    subcategories: [],
    subarticles: [],
    cache: {},
    articlesProcessed: 0,
    },

    methods: {
    submit: async function () {
        let labels = {};
        let primaryFound = false;
        for (let i = 0; i < this.categories.length; i++) {
        if (document.getElementById("primary_" + String(i)).checked) {
            labels[this.categories[i]["id"]] = 2;
            primaryFound = true;
        } else if (
            document.getElementById("secondary_" + String(i)).checked
        ) {
            labels[this.categories[i]["id"]] = 1;
        } else {
            labels[this.categories[i]["id"]] = 0;
        }
        }

        if (!primaryFound) {
        alert("Must label at least one primary");
        } else {
        for (let i = 0; i < this.subarticles.length; i++) {
            let article = this.subarticles[i];
            let art = {
            name: article["title"],
            labels: labels,
            };
            this.cache[String(article["pageid"])] = art;
            this.articlesProcessed += 1;
        }

        await this.reset();
        }
    },

    getSpecificCat: async function() {
        const title = document.getElementById("catName").value;
        await this.updateWithCatName(title);
    },

    save: function () {
        this.articlesProcessed = 0;
        let data = [
        [
            "id",
            "name",
            "ENTR",
            "HIST",
            "NSCI",
            "TECH",
            "ECMY",
            "SSCI",
            "HLTH",
            "CSMR",
            "GOVM",
            "RELG",
            "CULT",
            "FOOD",
            "SPRT",
            "GEOG",
            "ECOL",
            "PPLE",
        ],
        ];
        let keys = Object.keys(this.cache);

        for (let i = 0; i < keys.length; i++) {
        let item = this.cache[keys[i]];
        data.push([
            keys[i],
            JSON.stringify(item["name"]),
            item["labels"]["ENTR"],
            item["labels"]["HIST"],
            item["labels"]["NSCI"],
            item["labels"]["TECH"],
            item["labels"]["ECMY"],
            item["labels"]["SSCI"],
            item["labels"]["HLTH"],
            item["labels"]["CSMR"],
            item["labels"]["GOVM"],
            item["labels"]["RELG"],
            item["labels"]["CULT"],
            item["labels"]["FOOD"],
            item["labels"]["SPRT"],
            item["labels"]["GEOG"],
            item["labels"]["ECOL"],
            item["labels"]["PPLE"],
        ]);
        }
        let csvContent =
        "data:text/csv;charset=utf-8," +
        data.map((e) => e.join(",")).join("\n");
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `data_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
    },

    updateWithCatName: async function(name) {
        const parse = await getArticlesUnderCategory(name);

        await new Promise(r => setTimeout(r, 300));
        console.log(parse["articles"].length)
        console.log(name)

        if (parse["articles"].length < 3) {
            return false;
        }
        this.categoryName = name;
        this.subarticles = parse["articles"];
        this.subcategories = parse["subcats"];

        return true;
    },

    reset: async function () {

        let outerCriteriaMet = false;

        while (!outerCriteriaMet) {

        let criteriaMet = false;
        let name = '';

        while (!criteriaMet) {
            let articles = await getRandomArticles();
            for (let i = 0; i < articles.length; i++) {
            if (articles[i]["ns"] == 14) {
                name = articles[i]["title"];
                criteriaMet = true;
                break;
            }
            }
        }

        //this.categoryName = await getRandomCategory(article['title'])
        outerCriteriaMet = await this.updateWithCatName(name)
        }

        this.resetSelections();
    },

    resetSelections: function () {
        this.clearSel("categorySel1");
        this.clearSel("categorySel2");
    },

    clearSel: function (tag) {
        let ele = document.getElementsByName(tag);
        for (let i = 0; i < ele.length; i++) {
        ele[i].checked = false;
        }
    },
    },

    created: async function () {
    await this.reset();
    },
});
