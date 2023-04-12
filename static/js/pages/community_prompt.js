import Vue from 'vue/dist/vue.esm.js';

import { MarathonBuilder } from '../modules/prompts/marathon-submit.js';
import { SprintBuilder } from '../modules/prompts/sprint-submit.js';

var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    components: {
        'marathon-builder': MarathonBuilder,
        'sprint-builder': SprintBuilder
    }
}); // End vue