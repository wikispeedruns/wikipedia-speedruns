/**
 * File to define all the filters used in the game.
 */

const pathArrowFilter = (arr) => arr.map((pathEntry) => pathEntry["article"]).join(' → ');

export {pathArrowFilter};
