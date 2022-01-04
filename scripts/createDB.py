import pymysql
import json

# TODO Probably want to do this at some point
# http://jan.kneschke.de/projects/mysql/order-by-rand/
# TODO add indexes

DB_NAME='wikipedia_speedruns'

CREATE_DB_QUERY = 'CREATE DATABASE IF NOT EXISTS {}'.format(DB_NAME)
USE_DB_QUERY = 'USE {}'.format(DB_NAME)

TABLES={}

TABLES['users']=(
'''
CREATE TABLE IF NOT EXISTS `users` (
    `user_id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(20) NOT NULL UNIQUE,
    `hash` CHAR(60),
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `email_confirmed` BOOLEAN NOT NULL DEFAULT 0,
    `join_date` DATE NOT NULL,
    `admin` BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (`user_id`)
);
''')

# Add info for better calculations
TABLES['ratings']=(
'''
CREATE TABLE IF NOT EXISTS `ratings` (
    `user_id` INT NOT NULL,
    `rating` INT NOT NULL,
    `num_rounds` INT NOT NULL,
    PRIMARY KEY (`user_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);
'''
)

TABLES['prompts']=(
'''
CREATE TABLE IF NOT EXISTS `prompts` (
    `prompt_id` INT NOT NULL AUTO_INCREMENT,
    `start` VARCHAR(255) NOT NULL,
    `end` VARCHAR(255) NOT NULL,
    `public` BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (`prompt_id`)
);
''')

TABLES['runs']=(
'''
CREATE TABLE IF NOT EXISTS `runs` (
    `run_id` INT NOT NULL AUTO_INCREMENT,
    `start_time` TIMESTAMP(3) NOT NULL,
    `end_time` TIMESTAMP(3) NULL,
    `path` TEXT NULL,
    `prompt_id` INT NOT NULL,
    `user_id` INT,
    PRIMARY KEY (`run_id`),
    FOREIGN KEY (`prompt_id`) REFERENCES `prompts`(`prompt_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);
''')


def create_tables(cursor):
    for table in TABLES:
        cursor.execute(TABLES[table])

# Load database settings
config = json.load(open("../config/default.json"))
try:
    config.update(json.load(open("../config/prod.json")))
except FileNotFoundError:
    pass

conn = pymysql.connect(
    user=config["MYSQL_USER"], 
    host=config["MYSQL_HOST"],
    password=config["MYSQL_PASSWORD"]
)

with conn.cursor() as cursor:
    cursor.execute(CREATE_DB_QUERY)
    cursor.execute(USE_DB_QUERY)
    create_tables(cursor)
    
    conn.commit()
    conn.close()

