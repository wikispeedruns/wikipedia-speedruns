import pymysql

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

TABLES['attempts']=(
'''
CREATE TABLE IF NOT EXISTS `attempts` (
    `attempt_id` INT(11) NOT NULL AUTO_INCREMENT,
    `start` VARCHAR(255) NOT NULL,
    `prompt_id` INT(11) NOT NULL,
    PRIMARY KEY (`attempt_id`),
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

