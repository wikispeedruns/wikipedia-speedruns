delete marathonruns from marathonruns
LEFT JOIN users on marathonruns.user_id = users.user_id
where users.user_id is NULL and marathonruns.user_id IS NOT NULL;

ALTER TABLE marathonruns
ADD FOREIGN KEY (user_id) REFERENCES users(user_id);