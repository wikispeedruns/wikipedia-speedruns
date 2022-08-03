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
            highlightIndex: -1,
            timer: null
        }
	},

    methods: {
        async setAutocomplete() {
            this.acList = await getAutoCompleteArticles(this.text);
            this.open();
        },

        async updateText(text) {
            this.close();
            await this.$emit('update:text', text);
        },

        clearList() {
            this.acList = [];
        },

        async input(text) {
            this.clearList();
            await this.updateText(text);
            clearTimeout(this.timer);
            this.timer = setTimeout(this.setAutocomplete, 650);
        },

        async selectArticle(article) {
            if(!this.showAutocomplete) return;
            await this.updateText(article);
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

        focusout() {
            this.close();
            clearTimeout(this.timer);
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
        <div ref="list" style="width:auto">
            <input
                class="form-control"
                type="text"
                autocomplete=off
                :placeholder="placeholder"
                :value="text" 
                @input="input($event.target.value)" 
                @focusout="focusout"
                @keydown.enter.prevent="selectArticle(acList[highlightIndex])"
                @keydown.down.prevent="down"
                @keydown.up.prevent="up"
            />

            <div style="position:relative">
                <ul v-show="showAutocomplete"
                style="display:block; background-color:white; border: 1px solid #ddd; list-style:none; padding:0; position:absolute; left:0; top:100%; width:100%; z-index:1000;"
                >
                    <li v-for="(article, index) in acList"
                        @mousedown.prevent
                        @mouseover="setHighlightIndex(index)"
                        @click="selectArticle(article)"
                        :style="{ 'cursor':'pointer', 'background-color': index===highlightIndex ? 'lightgray':'transparent', 'padding':'0' }"
                    >
                        <h6 style="margin-left: 12px">{{ article }}</h6>
                    </li>
                </ul>
            </div>

            <div style="margin-bottom: 7px"></div>
        </div>  
    `)
};

export { autocompleteInput }