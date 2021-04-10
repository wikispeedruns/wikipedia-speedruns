import pymysql
# Probably want to do this at some point
# http://jan.kneschke.de/projects/mysql/order-by-rand/

DB_NAME='wikipedia_speedruns'

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

conn = pymysql.connect(user='user', host='127.0.0.1',
                            database=DB_NAME)

with conn.cursor() as cursor:
    create_tables(cursor)
    conn.commit
    conn.close()

