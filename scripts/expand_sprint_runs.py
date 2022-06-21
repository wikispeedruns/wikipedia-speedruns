import argparse
import json
import pymysql

DEFAULT_DB_NAME='wikipedia_speedruns'

def expand(db_name):

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

        query = "ALTER TABLE sprint_runs ADD COLUMN counted_for_achievements BOOLEAN DEFAULT 0"

        try:
            cursor.execute(query)
        except:
            print("'counted_for_achievements' already present in sprint_runs")
            return
        
        conn.commit()
        conn.close()

    print("sprint runs expanded to include 'counted_for_achievements'")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Adds all defined achievements in "achievement_functions" to database')
    parser.add_argument('--db_name', type = str, default = DEFAULT_DB_NAME)

    args = parser.parse_args()
    expand(args.db_name)