import pymysql
import json

import argparse
import os

DEFAULT_DB_NAME='wikipedia_speedruns'


def create_database(db_name, recreate=False):
    # Load database settings
    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"], 
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
    )

    with conn.cursor() as cursor:
        if (recreate):
            drop_db_query = f'DROP DATABASE {db_name}'
            cursor.execute(drop_db_query)

        create_db_query = f'CREATE DATABASE IF NOT EXISTS {db_name}'
        cursor.execute(create_db_query)
        use_db_query = f'USE {db_name}'
        cursor.execute(use_db_query)

        with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
            sql = f.read()

            for query in sql.split(';'):
                if len(query.strip()) == 0: continue
                cursor.execute(query)

        conn.commit()
        conn.close()



TABLES['marathonprompts']=(
'''
CREATE TABLE IF NOT EXISTS `marathonprompts` (
    `prompt_id` INT NOT NULL AUTO_INCREMENT,
    `start` VARCHAR(255) NOT NULL,
    `initcheckpoints` TEXT NOT NULL,
    `checkpoints` TEXT NOT NULL,
    `public` BOOLEAN NOT NULL DEFAULT 0,
    `seed` INT NOT NULL, 
    PRIMARY KEY (`prompt_id`)
);
''')

TABLES['marathonruns']=(
'''
CREATE TABLE IF NOT EXISTS `marathonruns` (
    `run_id` INT NOT NULL AUTO_INCREMENT,
    `path` TEXT NOT NULL,
    `checkpoints` TEXT NOT NULL,
    `prompt_id` INT NOT NULL,
    `user_id` INT,
    PRIMARY KEY (`run_id`)
);
''')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create the db for wikispeedruns.')
    parser.add_argument('--db_name', default=DEFAULT_DB_NAME)
    parser.add_argument('--recreate', action='store_true')

    args = parser.parse_args()
    create_database(args.db_name, recreate=args.recreate)

