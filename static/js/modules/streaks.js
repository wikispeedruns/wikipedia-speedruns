

function generateStreakText(data)
{

    if (data['streak'] == 0) {
        return "You currently don't have an active streak. Play the Prompt of the Day to start your streak!";
    }
    let first_blurbs = {
        5: `You currently have a 🔥<b> ${data['streak']} day streak </b>🔥, keep it up!`,
        10: `Good to see you again! You currently have a 🔥<b> ${data['streak']} day streak </b>🔥, impressive!`,
        25: `Woah, 🔥<b> ${data['streak']} day streak </b>🔥 and going strong!!`,
    };

    let disp = `Didn't think you'd make it this far, but you did! 🔥<b> ${data['streak']} day streak </b>🔥!!`
    for (const threshold in first_blurbs) {
        if (data['streak'] <= threshold) {
            disp = first_blurbs[threshold];
            break;
        }
    }

    let last = data['done_today'] == 1 ? ` You've played today's Prompt of the Day. Come back tomorrow to continue your journey.` : ` Play today's Prompt of the Day before it expires to continue your streak!`

    return disp + "<br>" +last;

}

export { generateStreakText };