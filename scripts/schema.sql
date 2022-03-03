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
    `join_date` DATE NOT NULL DEFAULT (CURRENT_DATE()),
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