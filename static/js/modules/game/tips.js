function getRandTip() {
    const tips = [
        "There are five permanent members of the UN security council: China, France, Russia, United Kingdom, and the United States.",
        "The Fortune magazine has a list for top 500 United States companies (“Fortune 500”), as well as a list for top 500 global companies (“Fortune Global 500”).",
        "Brazil is currently the world’s largest producer of sugarcane, and by a lot!",
        "Buddhism originated in ancient India sometime between the 6th and 4th centuries BCE.",
        "Pressing the back button will forfeit your attempt!",
        "Infoboxes on the right often give very quick and useful links, especially for biographical and geographical pages.",
        "Plan ahead, but be flexible! If you foresee a better route than what you had planned, go for it!",
        "Use the Table of Contents to your advantage!",
        "Some article subsections have an associated main article, usually linked under the subsection title."
    ];

    return tips[Math.floor(Math.random() * tips.length)];
}

export { getRandTip };