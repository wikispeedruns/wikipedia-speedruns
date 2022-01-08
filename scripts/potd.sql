
ALTER TABLE prompts MODIFY 
`type` ENUM ('unused', 'public', 'daily') NOT NULL DEFAULT 'public';

ALTER TABLE prompts MODIFY 
`type` ENUM ('unused', 'public', 'daily') NOT NULL DEFAULT 'unused';

UPDATE prompts SET `type`='unused' WHERE `public`=0;

SELECT * FROM prompts;
