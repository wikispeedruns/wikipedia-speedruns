import Vue from "vue/dist/vue.esm.js";

import { ArticleRenderer } from "../../modules/game/articleRenderer.js";
import { basicCannon } from "../../modules/confetti.js";

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        article: "",
        message: "",
        renderer: null,
    },

    methods: {
        async loadArticle() {
            this.renderer.loadPage(this.article);
        },

        pageCallback(article, loadTime) {
            this.message = (`'${article}' took ${loadTime/1000} seconds to load`);
            console.log(this.message);

            basicCannon(0, 0, false, 315)
            basicCannon(1, 0, false, 225)
        }
    },

    mounted: function() {
        let frame = document.getElementById("testFrame");
        this.renderer = new ArticleRenderer(frame, this.pageCallback);
    }
});
