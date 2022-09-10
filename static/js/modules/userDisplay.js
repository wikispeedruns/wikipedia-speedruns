
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

    methods: {
        goToProfile() {
            window.location.replace(this.link);
        }
    },

    mounted: function() {
        this.link = `/profile/${this.username}`;
    },

    template: (`
        <a :style="{ 'cursor': 'pointer', 'font-weight': bolded ? 'bold' : 'initial' }" @click.stop="goToProfile">{{username}}</a>
    `)
};

export { UserDisplay };