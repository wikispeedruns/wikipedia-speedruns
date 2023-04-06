INSERT INTO users (user_id, username, email, join_date) 
VALUES (-1, '%%ADMIN%%', 'adminadminadmin', '2023-01-01T00:00:00.000000');

ALTER TABLE sprint_prompts 
ADD cmty_added_by INT NOT NULL DEFAULT -1, 
ADD cmty_anonymous BOOL NOT NULL DEFAULT TRUE, 
ADD cmty_submitted_time TIMESTAMP(3)
ADD FOREIGN KEY (cmty_added_by) REFERENCES users(user_id);

