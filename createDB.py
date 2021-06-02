import pymysql
# Probably want to do this at some point
# http://jan.kneschke.de/projects/mysql/order-by-rand/

DB_NAME='wikipedia_speedruns'

CREATE_DB_QUERY = 'CREATE DATABASE IF NOT EXISTS {}'.format(DB_NAME)
USE_DB_QUERY = 'USE {}'.format(DB_NAME)

TABLES={}

TABLES['prompts']=(
'''
CREATE TABLE IF NOT EXISTS `prompts` (
    `prompt_id` INT(11) NOT NULL AUTO_INCREMENT,
    `start` VARCHAR(255) NOT NULL,
    `end` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`prompt_id`) 
);
''')

TABLES['runs']=(
'''
CREATE TABLE IF NOT EXISTS `runs` (
    `run_id` INT(11) NOT NULL AUTO_INCREMENT,
    `start_time` TIMESTAMP(3) NOT NULL,
    `end_time` TIMESTAMP(3) NOT NULL,
    `path` TEXT NOT NULL,
    `prompt_id` INT(11) NOT NULL,
    `name` TEXT NOT NULL,
    PRIMARY KEY (`run_id`),
    FOREIGN KEY (`prompt_id`) REFERENCES `prompts`(`prompt_id`)
);
''')

def create_tables(cursor):
    for table in TABLES:
        cursor.execute(TABLES[table])

conn = pymysql.connect(user='user', host='127.0.0.1')

with conn.cursor() as cursor:
    cursor.execute(CREATE_DB_QUERY)
    cursor.execute(USE_DB_QUERY)
    create_tables(cursor)
    
    conn.commit()
    conn.close()

