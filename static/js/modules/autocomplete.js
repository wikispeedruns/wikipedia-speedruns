import { getAutoCompleteArticles } from "./wikipediaAPI/util.js";

const count = 5;

var autocompleteInput = {

    props: {
        text: {
            type: String,
            default: ""
        },
        placeholder: {
            type: String,
            default: "Type in an article..."
        }
    },

    emits: ['update:text'],

    data: function () {
        return {
            acList: [],
            showAutocomplete: false,
            highlightIndex: -1
        }
	},

    methods: {
        async setAutocomplete() {
            this.acList = await getAutoCompleteArticles(this.text);
        },

        async updateText(text) {
            await this.$emit('update:text', text);
            await this.setAutocomplete();
            this.open();
        },

        async selectArticle(article) {
            if(!this.showAutocomplete) return;
            await this.updateText(article);
            this.close();
            this.$refs.list.focus();
        },

        up() {
            if(this.showAutocomplete){
                if(this.highlightIndex > 0){
                    this.highlightIndex --;
                }
                else{
                    this.close();
                }
            }
        },

        down() {
            if(this.showAutocomplete){
                if(this.highlightIndex < count - 1){
                    this.highlightIndex ++;
                }
            }
            else{
                this.open();
            }
        },

        open() {
            this.showAutocomplete = true;
            this.highlightIndex = 0;
        },

        close() {
            this.showAutocomplete = false;
        },

        setHighlightIndex(index){
            this.highlightIndex = index;
        }
    },

    template: (`
        <div ref="list">
            <input
                class="form-control" 
                type="text"
                autocomplete=off
                :placeholder="placeholder"
                :value="text" 
                @input="updateText($event.target.value)" 
                @focusout="close"
                @keydown.enter="selectArticle(acList[highlightIndex])"
                @keydown.down.prevent="down"
                @keydown.up.prevent="up"
            />

            <ul class="suggestion-list" v-show="showAutocomplete"
            style="display: block; border: 1px solid #ddd; list-style: none; padding: 0;"
            >
                <li v-for="(article, index) in acList"
                    @mousedown.prevent
                    @mouseover="setHighlightIndex(index)"
                    @click="selectArticle(article)"
                    :style="{ 'cursor': 'pointer', 'background-color': index===highlightIndex ? 'lightgray' : 'transparent' }"
                >
                    <h6 style="margin-left: 0.8em">{{ article }}</h6>
                </li>
            </ul>

            <div style="margin-bottom: 0.5em"></div>
        </div>  
    `)
};

export { autocompleteInput }