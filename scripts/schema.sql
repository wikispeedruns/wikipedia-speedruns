-- TODO Might want to do this at some point/
-- http://jan.kneschke.de/projects/mysql/order-by-rand/
-- TODO add indexes

CREATE TABLE IF NOT EXISTS `users` (
    `user_id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(20) NOT NULL UNIQUE,
    `hash` CHAR(60),
    `is_old_hash` BOOLEAN DEFAULT 0,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `email_confirmed` BOOLEAN NOT NULL DEFAULT 0,
    `join_date` DATE NOT NULL,
    `admin` BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (`user_id`)
);

CREATE TABLE IF NOT EXISTS `sprint_prompts` (
    `prompt_id` INT NOT NULL AUTO_INCREMENT,
    `start` VARCHAR(255) NOT NULL,
    `end` VARCHAR(255) NOT NULL,
    `rated` BOOLEAN NOT NULL DEFAULT 0,
    `active_start` DATETIME NULL,
    `active_end` DATETIME NULL,
    `used` BOOLEAN AS (NOT (active_start IS NULL OR active_end IS NULL)) VIRTUAL,
    PRIMARY KEY (`prompt_id`),
    INDEX (`active_start`, `active_end`)
);

CREATE TABLE IF NOT EXISTS `sprint_runs` (
    `run_id` INT NOT NULL AUTO_INCREMENT,
    `start_time` TIMESTAMP(3) NULL,
    `end_time` TIMESTAMP(3) NULL,
    `path` JSON NULL,
    `prompt_id` INT NOT NULL,
    `user_id` INT,
    PRIMARY KEY (`run_id`),
    FOREIGN KEY (`prompt_id`) REFERENCES `sprint_prompts`(`prompt_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);


CREATE TABLE IF NOT EXISTS `marathonprompts` (
    `prompt_id` INT NOT NULL AUTO_INCREMENT,
    `start` VARCHAR(255) NOT NULL,
    `initcheckpoints` TEXT NOT NULL,
    `checkpoints` TEXT NOT NULL,
    `public` BOOLEAN NOT NULL DEFAULT 0,
    `seed` INT NOT NULL, 
    PRIMARY KEY (`prompt_id`)
);

CREATE TABLE IF NOT EXISTS `marathonruns` (
    `run_id` INT NOT NULL AUTO_INCREMENT,
    `path` TEXT NOT NULL,
    `checkpoints` TEXT NOT NULL,
    `prompt_id` INT NOT NULL,
    `user_id` INT,
    `finished` BOOLEAN DEFAULT 1,
    `total_time` FLOAT(10) NOT NULL,
    PRIMARY KEY (`run_id`)
);

-- Tables for private lobbys
CREATE TABLE IF NOT EXISTS `lobbys` (
    `lobby_id` INT NOT NULL AUTO_INCREMENT, -- Internal
    `name` VARCHAR(50) NULL,
    `desc` VARCHAR(200) NULL,
    `passcode` VARCHAR(16) NOT NULL,     -- Not a hash, should be auto genearted
    `create_date` DATETIME NOT NULL,
    `active_date` DATETIME NULL,
    `rules` JSON NULL,
    PRIMARY KEY (`lobby_id`)
);

CREATE TABLE IF NOT EXISTS `user_lobbys` (
    `user_id` INT NOT NULL,
    `lobby_id` INT NOT NULL,
    `owner` BOOLEAN DEFAULT 0,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`),
    FOREIGN KEY (`lobby_id`) REFERENCES `lobbys`(`lobby_id`)
);

CREATE TABLE IF NOT EXISTS `lobby_prompts` (
    `lobby_id` INT,
    `prompt_id` INT NOT NULL,
    `start` VARCHAR(255) NOT NULL,
    `end` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`lobby_id`, `prompt_id`),
    FOREIGN KEY (`lobby_id`) REFERENCES `lobbys`(`lobby_id`)
);

CREATE TABLE IF NOT EXISTS `lobby_runs` (
	`run_id` INT NOT NULL AUTO_INCREMENT, -- Internal

    `lobby_id` INT,
    `prompt_id` INT NOT NULL,

    -- Either user_id or name should be not null, (but not both)
	`user_id` INT NULL,
    `name` VARCHAR(20)  NULL,

    `start_time` TIMESTAMP(3) NOT NULL,
    `end_time` TIMESTAMP(3) NOT NULL,
    `path` JSON NOT NULL,

    PRIMARY KEY (`run_id`),
    FOREIGN KEY (`lobby_id`, `prompt_id`) REFERENCES `lobby_prompts`(`lobby_id`, `prompt_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);


-- Public Ratings
CREATE TABLE IF NOT EXISTS `ratings` (
    `user_id` INT NOT NULL,
    `rating` INT NOT NULL,
    `num_rounds` INT NOT NULL,
    PRIMARY KEY (`user_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);


CREATE TABLE IF NOT EXISTS `historical_ratings` (
    `user_id` INT NOT NULL,
    `prompt_id` INT NOT NULL,
    `prompt_date` DATE NOT NULL,
    `prompt_rank` INT NOT NULL,
    `rating` INT NOT NULL,
    PRIMARY KEY (`user_id`, `prompt_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`),
    FOREIGN KEY (`prompt_id`) REFERENCES `sprint_prompts`(`prompt_id`),
    INDEX (`prompt_id`, `rating`)
);