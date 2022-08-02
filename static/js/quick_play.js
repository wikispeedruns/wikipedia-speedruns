import { getGeneratedPrompt } from "./modules/generator.js"
import { articleCheck } from "./modules/wikipediaAPI/util.js";

const difficulty = 1000;

let app = new Vue({
    el: '#app',

    mounted: async function() {
        let start = '', end = '';

        // loop until there is a valid start and end
        while(true){
            [start, end] = await getGeneratedPrompt(difficulty, 2);
            
            if(start == null || end == null || start === end) continue;
            
            console.log(start);
            console.log(end);

            const checkRes = await articleCheck(end);
            if (!('warning' in checkRes)) break;
        }

        console.log(`${start} -> ${end}`);
            
        const start_param = encodeURIComponent(start).replaceAll('%2F', '%252F');
        const end_param = encodeURIComponent(end).replaceAll('%2F', '%252F');

        window.location.replace(`/play/${start_param}/${end_param}`);
    }
});