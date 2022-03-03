var SavedMarathonGames = {

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
    <div class="row py-4">
        <div class="col px-0">
            <div class="card">
                <div class="card-body">
                    <h4>Your saved marathon games:</h4>
                    <table class="table table-hover">
                        <thead>
                            <th scope="col" class="px-2 py-2">Prompt #</th>
                            <th scope="col" class="px-2 py-2">Checkpoints Visited</th>
                            <th scope="col" class="px-2 py-2">Articles Visited</th>
                            <th scope="col" class="px-2 py-2">Clicks Remaining</th>
                            <th scope="col" class="px-2 py-2">Active Checkpoints</th>
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
                </div>
            </div>
        </div>
    </div>
    `)

};

export { SavedMarathonGames };
