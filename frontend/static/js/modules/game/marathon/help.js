
var MarathonHelp = {

    methods: {
        closeHelp: function () {
            this.$emit('close-help');
        }
    },
    template: (`
    <div id="help-box" class="HUDwrapper container">
        <div class="row flex-row flex-nowrap">
            <div class="col-9 px-4 py-2">
            <p><strong>NEW Marathon gamemode</strong></p>
            <p>In this new game mode, your objective is to go as far as you can with the limited amount of "clicks". 
                You will have 5 checkpoints that you can visit in any order. 
                Each checkpoint you manage to reach will give you 5 more clicks, and also give you a new checkpoint. 
                However, clicking on any link will cost 1 click. You will have won the game when you reach a certain number of checkpoints, but the game will end when you run out of clicks.</p>
                <p>Your score will depend on the total number of checkpoints you reach and the total number of unique articles you visit. You will be timed, but it will not factor into your score.</p>
                <p>You may forfeit your game at any point, and your progress thus far will be submitted as a complete run.</p>
                <p>Good luck!</p>
            <p></p>

            </div>
            <div class="col py-2 d-flex flex-row justify-content-end">
                <button v-on:click="closeHelp" class="btn btn-outline-secondary mt-auto align-self-end">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        </div>
    </div>
    `)

};

export { MarathonHelp };
