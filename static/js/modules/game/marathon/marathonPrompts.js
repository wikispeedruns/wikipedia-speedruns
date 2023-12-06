var MarathonPrompts = {

    props: ["prompts",
            "username"],

    data: function () {
        return {
            savedGames: []
        }
    },


    mounted: async function () {
        
        let keys = Object.keys(localStorage),
        i = keys.length;

        while ( i-- ) {
            if ( keys[i].substring(0, 5) == 'WS-M-') {
                this.savedGames.push( JSON.parse(localStorage.getItem(keys[i])) );
            }
        }

    },

    template: (`
        <div class="card">
            <div class="alert alert-info my-0" role="alert">
                <h5 class="my-0">Marathon Mode</h5>
                Tired of racing against the clock? Visit checkpoints to get more clicks—five for each. Keep going until your clicks run out.
            </div>
            <div class="card-body table-responsive">

                <p v-if="username">Check your marathon run history <a v-bind:href="'/marathonruns/' + username">here</a>.</p>

                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Prompt #</th>
                            <th scope="col">Starting Article</th>
                            <th scope="col">Starting Checkpoints</th>
                            <th scope="col">Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="prompt in prompts" v-cloak>
                            <td>{{prompt.prompt_id}} (<a v-bind:href="'/play/marathon/' + prompt.prompt_id">play</a>)</td>
                            <td>{{prompt.start}}</td>
                            <td>{{prompt.initcheckpoints}}</td>
                            <td>
                                <template v-if="prompt.username">
                                    <small>Community</small>
                                </template>
                                <template v-else class="text-muted">
                                    <small>Official</small>
                                </template>
                            </td>
                        </tr>
                    </tbody>
                </table>

                Pick up where you left off!

                <template v-if="savedGames.length > 0">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Prompt #</th>
                                <th scope="col">Checkpoints Visited</th>
                                <th scope="col">Articles Visited</th>
                                <th scope="col">Clicks Remaining</th>
                                <th scope="col">Active Checkpoints</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="game in savedGames" v-cloak>
                                <td>{{game.prompt_id}} (<a v-bind:href="'/play/marathon/' + game.prompt_id + '?load_save=1'">continue</a>)</td>
                                <td>{{game.visited_checkpoints.length}}</td>
                                <td>{{new Set(game.path).size}}</td>
                                <td>{{game.clicks_remaining}}</td>
                                <td>{{game.active_checkpoints}}</td>
                            </tr>
                        </tbody>
                    </table>
                </template>
                <template v-else>
                    You’re currently not running any marathons.
                </template>
            </div>
            <div class="card-footer text-muted">
                Save your runs to continue later. Want more? Check out our <b><a href="/marathon_archive" class="no-color">archive</a></b>.
            </div>
        </div>
    `)

};

export { MarathonPrompts };
