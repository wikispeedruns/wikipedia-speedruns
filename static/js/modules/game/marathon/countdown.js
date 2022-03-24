
import { getRandTip } from "../tips.js";

var CountdownTimer = {

    props: [
        "startArticle",
        "activeCheckpoints",
    ],

    data: function () {
        return {
            countdownDuration: 8000, // milliseconds to countdown from
            countdownRemaining: 8000,
            tip: "",

            started: false,
        }
    },


    mounted: async function () {
        this.tip = getRandTip();


        // Setup 2 conditions, when countdown finishes or when timer goes off.
        // Resolves when either condition resolves
        let countDownStart = Date.now();

        // Condition 1: countdown timer
        const promise1 = new Promise(resolve => {
            const x = setInterval(() => {
                const now = Date.now()

                // Find the distance between now and the count down date
                this.countdownRemaining = this.countdownDuration - (now - countDownStart);

                if (this.countdownRemaining <= -500) { //Allow timer to reach 0
                    resolve();
                    clearInterval(x);
                }


            }, 50);
        });

        // Condition 2: "immediate start" button click
        const promise2 = new Promise(r =>
            document.getElementById("start-btn").addEventListener("click", r, {once: true})
        )

        await Promise.any([promise1, promise2]);
        this.started = true;
        this.$emit('start-game');
    },

    template: (`
    <div v-show="!started">
        <div class="text-center text-size-1">
            <p>Starting Article: <strong>{{startArticle}}</strong></p>
            <p>Starting Checkpoints: <strong>{{activeCheckpoints}}</strong></p>
            <p>Good Luck!</p>

            <div><button id="start-btn" class="btn btn-outline-secondary">(Don't want to wait? Start immediately!)</button></div>
        </div>
        <div v-show="countdownRemaining < 700" class="mirroredimgblock">
            <img src="/static/assets/startgun.gif" class="startgun">
            <img src="/static/assets/startgun.gif" class="startgun invgif">
        </div>

        <div>
            <p id="countdown" class="countdown text-center mx-auto my-auto pb-5">{{ Math.floor(countdownRemaining/1000) + 1 }}</p>
        </div>

        <h6 id="tips" class="text-center">{{tip}}</h6>
    </div>
    `)

};

export { CountdownTimer };
