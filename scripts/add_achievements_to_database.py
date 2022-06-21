import argparse
import json
import pymysql

import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import wikispeedruns.achievements as achievements_utils

DEFAULT_DB_NAME='wikipedia_speedruns'



def add_achievements(db_name):

    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=db_name
    )

    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        achievements_utils.add_all_achievements(cursor)
        conn.commit()
        conn.close()

    print("all achievements added to database")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Adds all defined achievements in "achievement_functions" to database')
    parser.add_argument('--db_name', type = str, default = DEFAULT_DB_NAME)

    args = parser.parse_args()
    add_achievements(args.db_name)

    