var PagePreview = {

	props: {
		articlePreview: Object,
		clientX: Number,
		clientY: Number
	},

	methods: {
		computePosition: function() {
            const vh = window.innerHeight;
            const vw = window.innerWidth;
            const styleObject = {};

            if (vw >= 768) {
                if (this.clientX < vw / 2.0) {
                    styleObject['left'] = `${this.clientX+10}px`;
                } else {
                    styleObject['right'] = `${vw-this.clientX+10}px`;
                }
                if (this.clientY < vh / 2.0) {
                    styleObject['top'] = `${this.clientY+10}px`;
                } else {
                    styleObject['bottom'] = `${vh-this.clientY+10}px`;
                }
            } else {
                styleObject['left'] = `${Math.floor((vw-360)/2)}px`;
                styleObject['bottom'] = `${vh-this.clientY+25}px`;
            }
            return styleObject;
        }
	},

	template: (`
	<div class="tooltip-container" :style="computePosition()">
        <img v-if="articlePreview.thumbnail" :src="articlePreview.thumbnail.source" />
        <div v-html="articlePreview.extract_html"></div>
    </div>
	`)
};

export {PagePreview};
