import { getArticleSummary } from "../wikipediaAPI/util.js";

var PagePreview = {

    props: [
        'lang'
    ],

	data: function () {
        return {
            previewContent: null,
            eventTimestamp: null,
            eventType: null,
            clientX: 0,
            clientY: 0
        }
	},

	methods: {
        showPreview(e) {
            this.eventTimestamp = e.timeStamp;

            this.eventType = e.type;
            this.clientX = e.clientX;
            this.clientY = e.clientY;

            const href = e.currentTarget.getAttribute("href");
            const title = href.split('/wiki/').pop();
            const promises = [ getArticleSummary(title, this.lang) ];

            if (e.type !== "click") {
                promises.push(new Promise(resolve => setTimeout(resolve, 600)));
            }
            // const promise1 = getArticleSummary(title);
            // const promise2 = new Promise(resolve => setTimeout(resolve, 500));
            Promise.all(promises).then((values) => {
                if (e.timeStamp === this.eventTimestamp) {
                    this.previewContent = values[0];
                }
            });
        },

        hidePreview() {
            this.eventTimestamp = null;
            this.previewContent = null;
        },

		computePosition() {
            const vh = window.innerHeight;
            const vw = window.innerWidth;
            const styleObject = {};

            if (vw >= 768) {
                if (this.clientX < vw / 2.0) {
                    styleObject['left'] = `${this.clientX+10}px`;
                } else {
                    styleObject['right'] = `${vw-this.clientX+10}px`;
                }
            } else {
                styleObject['left'] = `${Math.floor((vw-360)/2)}px`;
            }
            if (this.clientY < vh / 2.0) {
                styleObject['top'] = `${this.clientY+10}px`;
            } else {
                styleObject['bottom'] = `${vh-this.clientY+10}px`;
            }
            return styleObject;
        }
	},

	template: (`
        <div v-if="previewContent">
            <div v-if="eventType === 'click'" class="blocker" @click="hidePreview"></div>

            <div class="tooltip-container" :style="computePosition()">
                <img v-if="previewContent.thumbnail" :src="previewContent.thumbnail.source" />
                <div v-html="previewContent.extract_html"></div>
            </div>
        </div>
	`)
};

export {PagePreview};
