
import Vue from "vue/dist/vue.esm.js";

import { PromptGenerator } from "../modules/generator.js"

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'prompt-generator': PromptGenerator,
    },

    data: {
        article: "Article",
    },

    methods: {
        async generateRndPrompt() {
            [ this.article ] = await this.$refs.pg.generatePrompt();
        },
    }

});
