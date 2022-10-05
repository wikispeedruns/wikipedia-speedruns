const confetti = require('canvas-confetti');

const defaultColors = [
    '#26ccff',
    '#a25afd',
    '#ff5e7e',
    '#88ff5a',
    '#fcff42',
    '#ffa62d',
    '#ff36ff'
  ];

function randomInt(min, max) {
// [min, max)
return Math.floor(Math.random() * (max - min)) + min;
}

function basicCannon(xi=0.5, yi=0.5, randomAngle=true, angle=90) {
    console.log("basicCannon")
    let defaults = { startVelocity: 30, spread: 90, ticks: 70, zIndex: 9999999, angle: randomAngle ? randomInt(55, 125) : angle, };
    let particleCount = 100;
    confetti(Object.assign({}, defaults, { particleCount, origin: { x: xi, y: yi } , color: defaultColors,zIndex: 9999999,}));
}

function fireworks(dur=5) {
    var duration = dur * 1000;
    var animationEnd = Date.now() + duration;
    var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    var interval = setInterval(function() {
    var timeLeft = animationEnd - Date.now();

    if (timeLeft <= 0) {
        return clearInterval(interval);
    }

    var particleCount = 50 * (timeLeft / duration);
    // since particles fall down, start a bit higher than random
    confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInt(0.1, 0.3), y: Math.random() - 0.2 } , color: defaultColors,zIndex: 250000,}));
    confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInt(0.7, 0.9), y: Math.random() - 0.2 } , color: defaultColors,zIndex: 250000,}));
    }, 250);
}

function side(dur=5) {
    var end = Date.now() + (dur * 1000);

    (function frame() {
    confetti({
        particleCount: 4,
        angle: 60,
        spread: 55,
        origin: { x: 0},
        color: defaultColors,
        zIndex: 250000,
    });
    confetti({
        particleCount: 4,
        angle: 120,
        spread: 55,
        origin: { x: 1},
        color: defaultColors,
        zIndex: 250000,
    });

    if (Date.now() < end) {
        requestAnimationFrame(frame);
    }
    }());
}


export { basicCannon, fireworks, side };