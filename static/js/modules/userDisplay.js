
var UserDisplay = {

    props: {
        username: String
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
        <a style="cursor:pointer" @click="goToProfile">{{username}}</a>
    `)
};

export { UserDisplay };