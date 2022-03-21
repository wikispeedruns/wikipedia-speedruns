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
    <div class="row pb-4">
        <div class="col px-0">
            <div class="card">
                <div class="alert alert-info my-0" role="alert">
                    Introducing our new <a href="#marathon-block" class="alert-link">Marathon</a> game mode. Give it a try!
                </div>
                <div class="card-body">
                    
                    <!--<h4>Marathon Prompts:</h4>-->
                    <p>
                        Every checkpoint you reach will buy you five more clicks and a new checkpoint, but every click you make on the way will cost one. There is no time limit on marathon mode - see how far you can go!
                    </p>

                    <p v-if="username">Check your marathon run history <a v-bind:href="'/marathonruns/' + username">here</a>.</p>

                    
                    <div v-if="savedGames.length > 0">
                        
                        <p>Here are your saved marathon games. Click 'continue' on any to get back into it!</p>

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
                        <hr class="mt-5">
                        <p>Click any prompt below to start a new marathon game. Any new saves you create will overwrite your previous save!</p>
                    </div>

                    

                    <table class="table table-hover">
                        <thead>
                            <th scope="col" class="px-2 py-2">Prompt #</th>
                            <th scope="col" class="px-2 py-2">Starting Article</th>
                            <th scope="col" class="px-2 py-2">Starting Checkpoints</th>
                        </thead>
                        <tbody>
                            <tr v-for="prompt in prompts" v-cloak>
                                <td>{{prompt.prompt_id}} (<a v-bind:href="'/play/marathon/' + prompt.prompt_id">play</a>)</td>
                                <td>{{prompt.start}}  </td>
                                <td>{{prompt.initcheckpoints}}  </td>
                            </tr>
                        </tbody>
                    </table>

                    

                    
                </div>
            </div>
        </div>
    </div>
    `)

};

export { MarathonPrompts };
