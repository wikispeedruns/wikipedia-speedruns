ALTER TABLE sprint_prompts 
ADD cmty_added_by INT DEFAULT NULL, 
ADD cmty_anonymous BOOL NOT NULL DEFAULT TRUE, 
ADD cmty_submitted_time TIMESTAMP(3),
ADD FOREIGN KEY (cmty_added_by) REFERENCES users(user_id);

ALTER TABLE marathonprompts 
ADD cmty_added_by INT DEFAULT NULL, 
ADD cmty_anonymous BOOL NOT NULL DEFAULT TRUE, 
ADD cmty_submitted_time TIMESTAMP(3),
ADD FOREIGN KEY (cmty_added_by) REFERENCES users(user_id);

