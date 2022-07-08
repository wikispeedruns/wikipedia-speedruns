import pymysql
import argparse
import json

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
        
        query = """
        ALTER TABLE sprint_runs
        ADD COLUMN `counted_for_am` BOOLEAN DEFAULT 0
        """
        cursor.execute(query)
        print("Column added")
        
        conn.commit()
        conn.close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Add a `counted_for_am` column to sprint_runs")
    parser.add_argument('--db_name', type = str, default = DEFAULT_DB_NAME)

    args = parser.parse_args()
    expand(args.db_name)