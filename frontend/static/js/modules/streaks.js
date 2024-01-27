

function generateStreakText(data)
{

    if (data['streak'] == 0) {
        return "You currently don't have an active streak. Play the Prompt of the Day to start your streak!";
    }

    let disp = ''

    if (data['streak'] <= 5) disp = `You currently have a 🔥<b> ${data['streak']} day streak </b>🔥, keep it up!`;
    else if (data['streak'] <= 10) disp = `Good to see you again! You currently have a 🔥<b> ${data['streak']} day streak </b>🔥, impressive!`;
    else if (data['streak'] <= 25) disp = `Woah, 🔥<b> ${data['streak']} day streak </b>🔥 and going strong!!`
    else `Didn't think you'd make it this far, but you did! 🔥<b> ${data['streak']} day streak </b>🔥!!`

    let last = data['done_today'] == 1 ? ` You've played today's Prompt of the Day. Come back tomorrow to continue your journey.` : ` Play today's Prompt of the Day before it expires to continue your streak!`

    return disp + "<br>" +last;

}

export { generateStreakText };