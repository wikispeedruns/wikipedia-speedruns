-- Run against the application database after reviewing the checkpoint replacement.
-- Idempotent; changes only prompt #22, never historical runs or browser saves.
START TRANSACTION;
UPDATE marathonprompts
SET initcheckpoints = REPLACE(initcheckpoints, '"Duffer brothers"', '"The Duffer Brothers"'),
    checkpoints = REPLACE(REPLACE(checkpoints, '"Prompt"', '"Prompt engineering"'),
                          '"Prompt (disambiguation)"', '"Prompt engineering"')
WHERE prompt_id = 22 AND start = 'Alexander the Great';
SELECT prompt_id, start, initcheckpoints, checkpoints
FROM marathonprompts WHERE prompt_id = 22;
COMMIT;
