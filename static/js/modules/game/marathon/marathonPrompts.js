var MarathonPrompts = {

    props: ["prompts",
            "username"],

    template: (`
    <div class="row py-4">
        <div class="col px-0">
            <div class="card">
                <div class="card-body">
                    <h4><b>NEW</b> Marathon prompts:</h4>
                    <p>Every checkpoint you reach will buy you five more clicks and a new checkpoint, but every click you make on the way will cost one. There is no time limit on marathon mode - see how far you can go!</p>

                    <table class="table table-hover">
                        <thead>
                            <th scope="col">Prompt #</th>
                            <th scope="col">Starting Article</th>
                            <th scope="col">Starting Checkpoints</th>
                        </thead>
                        <tbody>
                            <tr v-for="prompt in prompts" v-cloak>
                                <td>{{prompt.prompt_id}} (<a v-bind:href="'/play/marathon/' + prompt.prompt_id">play</a>)</td>
                                <td>{{prompt.start}}  </td>
                                <td>{{prompt.initcheckpoints}}  </td>
                            </tr>
                        </tbody>
                    </table>

                    <button v-if="username" v-on:click="window.location.replace('/marathonruns/' + username)" class="btn btn-outline-secondary mt-auto">Check your marathon run history</button>
                </div>
            </div>
        </div>
    </div>
    `)

};

export { MarathonPrompts };
