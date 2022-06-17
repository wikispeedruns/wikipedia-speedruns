import argparse
import json
import pymysql

import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import wikispeedruns.achievements as achievements_utils

"""
Considers all runs done by each of the users and adds information to database

1. Removes all existing achievements progress
2. Goes through the historical runs of each user and adds progress to database
"""

DEFAULT_DB_NAME='wikipedia_speedruns'


def remove_all_achievements_and_progress(cursor):
    cursor.execute("DELETE FROM achievements")
    cursor.execute("DELETE FROM achievements_progress")


def get_all_runs(cursor):
    query = """
    SELECT `start_time`, `end_time`, `play_time`, `path`, `user_id` FROM sprint_runs
    """
    cursor.execute(query)
    return list(cursor.fetchall())


def place_in_database(cursor, already_achieved, achievements_progress):
    
    list = []
    for key in already_achieved:
        list.append(
            {
                "user_id": key[0],
                "achievement_id": key[1],
                "time_achieved": already_achieved[key]
            }
        )

    query = """
    INSERT INTO achievements (achievement_id, user_id, time_achieved) 
    VALUES (%(achievement_id)s, %(user_id)s, %(time_achieved)s)
    """
    cursor.executemany(query, list)
    list.clear()

    for key in achievements_progress:
        list.append(
            {   
                "user_id": key[0],
                "achievement_id": key[1],
                "progress": achievements_progress[key]["progress"],
                "progress_as_number": achievements_progress[key]["progress_as_number"],
                "achieved": achievements_progress[key]["achieved"]
            }
        )

    query = """
    INSERT INTO achievements_progress (achievement_id, user_id, progress, progress_as_number, achieved)
    VALUES (%(achievement_id)s, %(user_id)s, %(progress)s, %(progress_as_number)s, %(achieved)s)
    """
    cursor.executemany(query, list)
    list.clear()



def process_run(single_run_data, achievements, already_achieved, achievements_progress):

    user_id = single_run_data["user_id"]
    single_run_article_map = {}

    for entry in single_run_data["path"]:
        article = entry["article"]
        if article in single_run_article_map:
            single_run_article_map[article] += 1
        else:
            single_run_article_map[article] = 1
    

    for id in achievements:

        key = (user_id, id)

        if key in already_achieved:
            continue

        current_progress = ""
        present_in_data = key in achievements_progress
        if achievements[id].is_multi_run_achievement and present_in_data:
            current_progress = achievements_progress[key]["progress"]
        
        achieved, new_progress, new_progress_as_number = achievements[id].check_status(single_run_data, single_run_article_map, current_progress)
        new_progress_as_string = json.dumps(new_progress)

        if achievements[id].is_multi_run_achievement:
            if present_in_data:
                achievements_progress[key]["progress"] = new_progress_as_string
                achievements_progress[key]["progress_as_number"] = new_progress_as_number
                achievements_progress[key]["achieved"] = achieved
            elif new_progress_as_string != achievements[id].default_progress:
                achievements_progress[key] = {
                    "achievement_id": id,
                    "user_id": user_id,
                    "progress": new_progress_as_string,
                    "progress_as_number": new_progress_as_number,
                    "achieved": achieved
                }        

        if achieved:
            already_achieved[key] = single_run_data["end_time"]



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

        remove_all_achievements_and_progress(cursor)
        
        achievements = {}
        achievements_utils.add_all_achievements(cursor, achievements) # places all the achievement information in achievements

        all_runs = get_all_runs(cursor)
        already_achieved = {} # maps from tuple(user_id, achievement_id) to time_achieved
        achievements_progress = {} # maps from tuple(user_id, achievement_id) to progress, progress_as_number, achieved

        for run_data in all_runs:
            process_run(achievements_utils.convert_to_standard(run_data), achievements, already_achieved, achievements_progress)
        
        place_in_database(cursor, already_achieved, achievements_progress)

        conn.commit()
        conn.close()
    
    print("Process Complete")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Considers all runs done by each user and adds information to database')
    parser.add_argument('--db_name', type = str, default = DEFAULT_DB_NAME)

    args = parser.parse_args()
    historical_achievements(args.db_name)

    