import argparse
import json
import pymysql

import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
next_parent = os.path.dirname(parent)
sys.path.append(next_parent)

import wikispeedruns.achievements as achievements_utils

"""
Considers all runs done by each of the users and adds information to database

1. Removes all existing achievements progress
2. Goes through the historical runs of each user and adds progress to database
"""

DEFAULT_DB_NAME='wikipedia_speedruns'


def remove_all_achievements_and_progress(cursor):
    cursor.execute("DELETE FROM achievements_progress")


def get_all_runs(cursor):
    query = """
    SELECT `start_time`, `end_time`, `play_time`, `finished`, `path`, `user_id`, `run_id` FROM sprint_runs WHERE user_id IS NOT NULL
    """
    cursor.execute(query)
    return list(cursor.fetchall())


def place_in_database(cursor, achievements_progress):
    achieved = []
    not_achieved = []
    for key in achievements_progress:
        entry = {
            "user_id": key[0],
            "achievement_id": key[1],
            "progress": achievements_progress[key]["progress"],
            "progress_as_number": achievements_progress[key]["progress_as_number"],
            "achieved": achievements_progress[key]["achieved"],
            "time_achieved": achievements_progress[key]["time_achieved"]
        }
        if achievements_progress[key]["achieved"]:
            achieved.append(entry)
        else:
            not_achieved.append(entry)

    query = """
    INSERT INTO achievements_progress (user_id, achievement_id, progress, progress_as_number, achieved, time_achieved)
    VALUES (%(user_id)s, %(achievement_id)s, %(progress)s, %(progress_as_number)s, %(achieved)s, %(time_achieved)s)
    """
    cursor.executemany(query, achieved)

    query = """
    INSERT INTO achievements_progress (user_id, achievement_id, progress, progress_as_number, achieved)
    VALUES (%(user_id)s, %(achievement_id)s, %(progress)s, %(progress_as_number)s, %(achieved)s)
    """
    cursor.executemany(query, not_achieved)



def process_run(single_run_data, achievements, achievements_progress):

    user_id = single_run_data["user_id"]
    single_run_article_map = {}

    for entry in single_run_data["path"]:
        article = entry["article"]
        if article in single_run_article_map:
            single_run_article_map[article] += 1
        else:
            single_run_article_map[article] = 1


    for achievement_id in achievements:

        key = (user_id, achievement_id)
        present_in_data = key in achievements_progress

        if present_in_data and achievements_progress[key]["achieved"]:
            continue

        current_progress = ""
        if present_in_data:
            current_progress = achievements_progress[key]["progress"]

        checked, progress_data = achievements[achievement_id].check_status(single_run_data, single_run_article_map, current_progress)
        achieved, new_progress, new_progress_as_number = progress_data

        if not checked:
            continue
        if not achievements[achievement_id].is_multi_run_achievement:
            if achieved:
                new_progress = new_progress_as_number = 1
            else:
                new_progress = new_progress_as_number = 0

        new_progress_as_string = json.dumps(new_progress)


        if present_in_data:
            achievements_progress[key]["progress"] = new_progress_as_string
            achievements_progress[key]["progress_as_number"] = new_progress_as_number
            achievements_progress[key]["achieved"] = achieved

        elif new_progress_as_string != achievements[achievement_id].default_progress:
            achievements_progress[key] = {
                "achievement_id": achievement_id,
                "user_id": user_id,
                "progress": new_progress_as_string,
                "progress_as_number": new_progress_as_number,
                "achieved": achieved,
                "time_achieved": None
            }

        if achieved:
            achievements_progress[key]["time_achieved"] = single_run_data["end_time"]


def set_all_sprint_runs(cursor, id_list):
    cursor.execute("UPDATE sprint_runs SET counted_for_am = 0")
    query = "UPDATE sprint_runs SET counted_for_am = 1 WHERE run_id IN {};".format(tuple(id_list))
    cursor.execute(query)


def historical_achievements(db_name):

    while True:
        val = input("Are you sure you want to reconsider all run data?: (yes/no)")
        if val.lower() == "yes":
            break
        elif val.lower() == "no":
            print("no changes were made")
            return
        else:
            print("This is not a valid format for (yes/no); try again")


    config = json.load(open("../../config/default.json"))
    try:
        config.update(json.load(open("../../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=db_name
    )

    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:

        remove_all_achievements_and_progress(cursor)
        achievements = achievements_utils.get_achievements_info(cursor)

        all_runs = get_all_runs(cursor)
        achievements_progress = {} # maps from tuple(user_id, achievement_id) to progress, progress_as_number, achieved, time_achieved
        id_list = [] # stores all runs that got considered
        failed = [] # stores all runs that failed

        for run_data in all_runs:
            run_id = run_data["run_id"]
            try:
                achievements_utils.check_data(run_data)
                process_run(achievements_utils.convert_to_standard(run_data), achievements, achievements_progress)
                id_list.append(run_id)
            except:
                failed.append(run_id)

        place_in_database(cursor, achievements_progress)
        set_all_sprint_runs(cursor, id_list)

        print("Failed to consider run_id {}".format(failed))

        conn.commit()
        conn.close()

    print("Process Complete")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Considers all runs done by each user and adds information to database')
    parser.add_argument('--db_name', type = str, default = DEFAULT_DB_NAME)

    args = parser.parse_args()
    historical_achievements(args.db_name)

