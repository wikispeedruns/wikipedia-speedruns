
var UserDisplay = {

    props: {
        username: String,
        bolded: {
            type: Boolean,
            default: false
        }
    },

    data: function () {
        return {
            link: ''
        }
	},

    mounted: function() {
        this.link = `/profile/${this.username}`;
    },

    template: (`
        <a :href="link" :style="{ 'color': 'inherit', 'cursor': 'pointer', 'font-weight': bolded ? 'bold' : 'initial' }" @click.stop="">{{username}}</a>
    `)
};

export { UserDisplay };