/*
    This file should have parity with the actual database.
    For any changes to the database, those changes should be reflected here.

    Schema Version: 2.4
    This version number should be incremented with any change to the schema.
    Keep this up-to-date with db.py
*/

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
    `play_time` FLOAT NULL,
    `finished` BOOLEAN DEFAULT 0,
    `path` JSON NULL,
    /*
    {
        "version": number
        "path": [
            ...
            {
                "article": string,
                "timeReached": number,
                "loadTime": number,
            },
            ...
        ]
    }
    */
    `prompt_id` INT NOT NULL,
    `user_id` INT,
    `counted_for_am` BOOLEAN DEFAULT 0,
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
    PRIMARY KEY (`run_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
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
    /*
    Schema for rules. In general, we need to be backwards compatible, so
    these should have default values or default behavior if the fields are missing
    {
        hide_prompt_end: (false)
        restrict_leaderboard_access: (false)
        require_account: (false)
    }
    */


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
    `language` VARCHAR(31) NOT NULL,
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

    `start_time` TIMESTAMP(3) NULL,
    `end_time` TIMESTAMP(3) NULL,
    `play_time` FLOAT NULL,
    `finished` BOOLEAN DEFAULT 0,
    `path` JSON NULL,
    /*
    {
        "version": number
        "path": [
            ...
            {
                "article": string,
                "timeReached": number,
                "loadTime": number,
            },
            ...
        ]
    }
    */

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

CREATE TABLE IF NOT EXISTS `list_of_achievements` (
    `achievement_id` INT NOT NULL AUTO_INCREMENT,
    `name` varchar(60) NOT NULL,
    PRIMARY KEY (`achievement_id`)
);

CREATE TABLE IF NOT EXISTS `achievements_progress` (
    `achievement_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `progress` JSON NOT NULL,
    `progress_as_number` INT NOT NULL,
    `achieved` BOOLEAN DEFAULT 0,
    `time_achieved` TIMESTAMP(3) NULL,
    PRIMARY KEY (`achievement_id`, `user_id`),
    FOREIGN KEY (`achievement_id`) REFERENCES `list_of_achievements`(`achievement_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);

CREATE TABLE IF NOT EXISTS `quick_runs` (
    `run_id` INT NOT NULL AUTO_INCREMENT,
    `start_time` TIMESTAMP(3) NULL,
    `end_time` TIMESTAMP(3) NULL,
    `play_time` FLOAT NULL,
    `finished` BOOLEAN DEFAULT 0,
    `path` JSON NULL,
    /*
    {
        "version": number
        "path": [
            ...
            {
                "article": string,
                "timeReached": number,
                "loadTime": number,
            },
            ...
        ]
    }
    */
    `prompt_start` VARCHAR(255) NOT NULL,
    `prompt_end` VARCHAR(255) NOT NULL,
    `language` VARCHAR(31) NOT NULL,
    `user_id` INT,
    PRIMARY KEY (`run_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);

-- Stats
CREATE TABLE IF NOT EXISTS `computed_stats` (
    `stats_json` JSON NOT NULL,
    /*
    {
        version: number - The database version number.
        stats: dict[stat_name: str, stat_val: number | Any] - See stats.py for list of included stats. Newer stats not guaranteed to be included in older runs.
    }
        example stats payload:
        stats: {
            .
            .
            daily_quick_runs: []
            daily_sprints: [{daily_plays: 41, day: "2022-11-09", total: "41"}, {daily_plays: 41, day: "2022-11-10", total: "82"},…]
            goog_total: 0
            lobbies_created: 41
            .
            .
        }
    */
    `timestamp` TIMESTAMP(3) NOT NULL,
    PRIMARY KEY (`timestamp`)      
);