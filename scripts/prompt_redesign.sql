INSERT INTO `sprint_prompts` (`prompt_id`, `start`, `end`, `rated`, `active_start`, `active_end`)
SELECT
    p.prompt_id, `start`, `end`,
    IF(d.rated IS NULL, 0, d.rated),
    IF(d.date IS NULL, DATE_ADD(CURDATE(), INTERVAL -10 DAY), d.date),
    IF(d.date IS NULL, DATE_ADD(CURDATE(), INTERVAL -9 DAY),  DATE_ADD(d.date, INTERVAL 1 DAY))
FROM prompts as p
LEFT JOIN daily_prompts as d ON p.prompt_id = d.prompt_id;

SELECT * FROM sprint_prompts;

INSERT INTO sprint_runs
SELECT * FROM runs;

SELECT * FROM sprint_runs;
