from distutils.util import convert_path
from textwrap import indent
import pymysql
import json

import argparse
import os

DEFAULT_DB_NAME='wikipedia_speedruns'


def convert_paths(db_name):
    # Load database settings from
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

    for table in ["sprint_runs", "lobby_runs"]:
        with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            query = f"SELECT run_id, path FROM {table}"
            cursor.execute(query)
            runs = cursor.fetchall()

            for run in runs:
                if run["path"] is None: continue
                path = json.loads(run["path"])
                if type(path) != list: continue

                path = {
                    "version": 1.0,
                    "path": [
                        {
                            "article": article,
                            "loadTime": 0,
                            "timeReached": 0
                        } for article in path
                    ]
                }
                run["path"] = json.dumps(path)

            query = f"UPDATE {table} SET path=%(path)s WHERE run_id=%(run_id)s"
            cursor.executemany(query, runs)
            conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create the db for wikispeedruns.')
    parser.add_argument('--db_name', default=DEFAULT_DB_NAME)

    args = parser.parse_args()
    convert_paths(args.db_name)

