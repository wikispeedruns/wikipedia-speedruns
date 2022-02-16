INSERT INTO `sprint_prompts` (`prompt_id`, `start`, `end`, `rated`, `active_start`, `active_end`)
SELECT 
	p.prompt_id, `start`, `end`, 
    IF(d.rated IS NULL, 0, d.rated), 
    IF(d.date IS NULL, CURDATE(), d.date), 
    DATE_ADD(IF(d.date IS NULL, CURDATE() + 7, d.date + 1), INTERVAL -1 SECOND)
FROM prompts as p
LEFT JOIN daily_prompts as d ON p.prompt_id = d.prompt_id;

SELECT * FROM sprint_prompts;

INSERT INTO sprint_runs
SELECT * FROM runs;

SELECT * FROM sprint_runs;