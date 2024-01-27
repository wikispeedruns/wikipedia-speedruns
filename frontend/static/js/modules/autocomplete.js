import { getAutoCompleteArticles } from "./wikipediaAPI/util.js";

const count = 5;

var AutocompleteInput = {

    props: {
        text: {
            type: String,
            default: ""
        },
        lang: {
            type: String,
            default: "en",
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
            lastInputTime: null,
            highlightIndex: -1,
            timer: null,
            timeout: 600
        }
	},

    methods: {
        async setAutocomplete(timeCalled) {
            this.acList = await getAutoCompleteArticles(this.text, this.lang);
            // only show if there was no recent inputs during the getting stage
            if(this.lastInputTime === timeCalled) this.open();
            else this.clearList();
        },

        updateText(text) {
            this.close();
            this.$emit('update:text', text);
        },

        clearList() {
            this.acList = [];
        },

        input(text) {
            this.lastInputTime = Date.now();

            this.clearList();
            this.updateText(text);

            clearTimeout(this.timer);
            this.timer = setTimeout(this.setAutocomplete.bind(null, this.lastInputTime), this.timeout);
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
            this.lastInputTime = Date.now();
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
        <div ref="list" class="col">
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
        </div>  
    `)
};

export { AutocompleteInput }