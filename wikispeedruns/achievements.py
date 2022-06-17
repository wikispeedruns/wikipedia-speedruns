from typing import List, Tuple, Dict, Any, Optional, Callable

import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from wikispeedruns.achievement_functions import place_all_achievements_in_list

import pymysql
from pymysql.cursors import DictCursor

import json


actual_data = {
    "end_time": "2022-05-27T10:22:25.446000",
    "path": [
      {
        "article": "45 (number)",
        "loadTime": 0.169,
        "timeReached": 0.169
      },
      {
        "article": "46 (number)",
        "loadTime": 0.135,
        "timeReached": 1.887
      }
    ],
    "play_time": 1.583,
    "run_id": 11631,
    "start_time": "2022-05-27T10:22:23.559000",
    "user_id": 5,
    "username": "dan"
}

test_data_1 = {
    "end_time": "2022-05-27T10:22:25.446000",
    "path": '{"path": [{"article": "45 (number)","loadTime": 0.169,"timeReached": 0.169},{"article": "46 (number)","loadTime": 0.135,"timeReached": 1.887}],"version": "2.1"}',
    "play_time": 1.583,
    "run_id": 11631,
    "start_time": "2022-05-27T10:22:23.559000",
    "user_id": 3,
    "username": "dan"
}

def version_2_1(test_data: Any) -> Dict[str, Any]:
    path = json.loads(test_data["path"])
    actual_data = dict.copy(test_data)
    actual_data["path"] = path["path"]
    return actual_data

def version_2_0(test_data: Any) -> Dict[str, Any]:
    return test_data

def version_1_0(test_data: Any) -> Dict[str, Any]:
    path = json.loads(test_data["path"])
    actual_data = dict.copy(test_data)
    actual_data["path"] = path["path"]
    return actual_data

def get_version_map():
    return {
        "1.0": version_1_0,
        "2.0": version_2_0,
        "2.1": version_2_1
    }

def convert_to_standard(test_data: Dict[str, Any]) -> Dict[str, Any]:
    version_map = get_version_map()
    path = json.loads(test_data["path"])
    version = path["version"]
    return version_map[version](test_data)






ReturnType = Tuple[bool, Any, Optional[int]]
AchievementFunction = Callable[[Dict[str, Any], Dict[str, int], str], ReturnType]

"""
*** Achievement Class ***

function: the check function that defines an achievement; different formats depending on type of achievement
is_multi_run_achievement: whether the achievement is a multiple run achievement
endgoal: stores the endgoal for this achievement in progress
default_progress: The value representing progress when no actual progress has been made (a definition of the data) * only useful for multiple run achievements
"""
class Achievement():
    def __init__(self, name: str, function: AchievementFunction, is_multi_run_achievement: bool, endgoal: int = 1, default_progress: str = "") -> None:
        self.name = name
        self.check_function = function
        self.is_multi_run_achievement = is_multi_run_achievement
        self.endgoal = endgoal
        self.default_progress = default_progress

    def check_status(self, single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
        if current_progress == "":
            current_progress = self.default_progress
        return self.check_function(single_run_data, single_run_article_map, json.loads(current_progress))


"""
Adds all the achievements present in the function

achievements: a dictionary mapping {achievement_id : achievement_object (defined in class above)}
"""
def add_all_achievements(cursor: DictCursor, achievements: Dict[int, Achievement]) -> None:
    list_of_achievements = place_all_achievements_in_list()
    for achievement in list_of_achievements:
        add_achievement(cursor, achievements, 
        achievement["name"], achievement["function"], achievement["is_multi_run_achievement"], achievement["endgoal"], achievement["default_progress"])


"""
Adds the achievement specified by the information

endgoal: the progress that will be shown when the achievement is complete (as a number)
default_progress: the progress that will be shown when no progress has been made
"""
def add_achievement(cursor: DictCursor, achievements: Dict[int, Achievement], 
name: str, function: AchievementFunction, is_multi_run_achievement: bool, endgoal: int = 1, default_progress: str = "") -> None:

    # Inserts achievement into database if not present, otherwise makes no change
    num_rows = cursor.execute("SELECT achievement_id FROM list_of_achievements WHERE name = (%s)", (name, ))
    if(num_rows == 0):
        cursor.execute("INSERT INTO list_of_achievements (name) VALUES (%s)", (name, ))
        cursor.execute("SELECT LAST_INSERT_ID() AS achievement_id")

    row = cursor.fetchone()
    id = -1
    if row is not None:
        id = row["achievement_id"]

    # Inserts achievement into achievements dictionary
    achievements[id] = Achievement(name, function, is_multi_run_achievement, endgoal, default_progress)



"""
returns all the new_achievements by the user after new run (using get_new_achievements)
and makes updates to achievements database accordingly (using add_achievements_to_database)
"""
def get_and_update_new_achievements(cursor: DictCursor, single_run_data: Dict[str, Any], achievements: Dict[int, Achievement]) -> List[int]:
    actual_data = convert_to_standard(single_run_data)
    new_achievements = get_new_achievements(cursor, actual_data, achievements)
    add_achievements_to_database(cursor, actual_data["user_id"], actual_data["end_time"], new_achievements)
    return new_achievements


"""
returns all the new_achievements by the user after new run
"""
def get_new_achievements(cursor: DictCursor, single_run_data: Dict[str, Any], achievements: Dict[int, Achievement]) -> List[int]:

    # Create single_run_article_map as defined above
    single_run_article_map: Dict[str, int] = {}
    for entry in single_run_data["path"]:
        article = entry["article"]
        if article in single_run_article_map:
            single_run_article_map[article] += 1
        else:
            single_run_article_map[article] = 1


    new_achievements = []
    user_id = single_run_data["user_id"]

    # stores a sorted array of achievement_id's already achieved
    already_achieved = get_already_achieved(cursor, user_id)

    # places all the present progress data for unachieved multi-run achievements 
    # into list_of_achievements_progress sorted by achievement_id
    list_of_achievements_progress = get_unachieved_multi_run_achievements(cursor, user_id)

    # j represents pointer in already_achieved
    # k represents pointer in list_of_achievements_progress
    # this is like two-pointer algorithm
    j, k = 0, 0


    # loop through all achievement_id's
    for id in sorted(achievements):
        
        # ignore achievements that are present in database but not present here
        while j < len(already_achieved) and already_achieved[j] < id:
            j += 1
        while k < len(list_of_achievements_progress) and list_of_achievements_progress[k]["achievement_id"] < id:
            k += 1
        

        # if this id is present in already_achieved, skip it
        if j < len(already_achieved) and already_achieved[j] == id:
            j += 1
            continue
        
        # gets the current progress for the achievement; None if it is not a multi-run achievement or it is not present in the database
        current_progress = ""
        present_in_database = k < len(list_of_achievements_progress) and list_of_achievements_progress[k]["achievement_id"] == id
        if achievements[id].is_multi_run_achievement and present_in_database:
            current_progress = list_of_achievements_progress[k]["progress"]

        # gets the new progress after considering the data
        achieved, new_progress, new_progress_as_number = achievements[id].check_status(single_run_data, single_run_article_map, current_progress)
        new_progress_as_string = json.dumps(new_progress)

        # for multi-run achievements:
        # updates progress status if it is already present in database
        # adds a new entry to the end otherwise as long as it is not empty progress
        if achievements[id].is_multi_run_achievement:
            if present_in_database:
                list_of_achievements_progress[k]["progress"] = new_progress_as_string
                list_of_achievements_progress[k]["progress_as_number"] = new_progress_as_number
                list_of_achievements_progress[k]["achieved"] = achieved
                k += 1
            elif new_progress_as_string != achievements[id].default_progress:
                list_of_achievements_progress.append(
                  {
                    "achievement_id": id,
                    "user_id": user_id,
                    "progress": new_progress_as_string,
                    "progress_as_number": new_progress_as_number,
                    "achieved": achieved
                  }
                )

        # put this achievement_id in the new_achievements if requirements are met
        if achieved:
            new_achievements.append(id)

    # Updates the achievements_progress table with the new progress data
    query = """
    INSERT INTO achievements_progress (achievement_id, user_id, progress, progress_as_number, achieved)
    VALUES (%(achievement_id)s, %(user_id)s, %(progress)s, %(progress_as_number)s, %(achieved)s)
    ON DUPLICATE KEY UPDATE progress = VALUES(progress), progress_as_number = VALUES(progress_as_number), achieved = VALUES(achieved)
    """
    cursor.executemany(query, list_of_achievements_progress)

    return new_achievements


"""
adds the new achievements achieved by user into database
"""
def add_achievements_to_database(cursor: DictCursor, user_id: int, time_achieved: str, achievement_ids: List[int]) -> None:

    query = "INSERT INTO achievements (achievement_id, user_id, time_achieved) VALUES (%s, %s, %s)"
    cursor.executemany(query, [(achievement_id, user_id, time_achieved) for achievement_id in achievement_ids])


"""
gets a sorted array of all the achievement_id's already achieved
"""
def get_already_achieved(cursor: DictCursor, user_id: int) -> List[int]:

    query = """
    SELECT achievement_id FROM achievements
    WHERE user_id = (%s)
    """
    cursor.execute(query, (user_id,))
    user_achieved = cursor.fetchall()
    return sorted([x['achievement_id'] for x in user_achieved])

"""
gets a list of all the unachieved multi-run achievements sorted by achievement_id
"""
def get_unachieved_multi_run_achievements(cursor: DictCursor, user_id: int) -> List[Dict[str, Any]]:
    query = """
    SELECT * FROM achievements_progress
    WHERE user_id = (%s) AND achieved = 0
    ORDER BY achievement_id
    """
    cursor.execute(query, (user_id,))
    return list(cursor.fetchall())


def get_all_achievements_and_progress(cursor: DictCursor, user_id: int, achievements: Dict[int, Achievement]) -> Dict[str, Dict[str, Any]]:

    # get all achievements achieved by the user with the time_achieved
    query = """
    SELECT achievement_id, time_achieved FROM achievements
    WHERE user_id = (%s)
    ORDER BY achievement_id
    """
    cursor.execute(query, (user_id,))
    already_achieved = list(cursor.fetchall())

    
    # get the progress data for multi-run achievements that are not achieved yet
    unachieved_multi_run_progress = get_unachieved_multi_run_achievements(cursor, user_id)

    # j represents pointer in already_achieved
    # k represents pointer in unachieved_multi_run_progress
    j, k = 0, 0
    all_achievements = {}

    for id in sorted(achievements):

        # ignore achievements that are present in database but not present here
        while j < len(already_achieved) and already_achieved[j]["achievement_id"] < id:
            j += 1
        while k < len(unachieved_multi_run_progress) and unachieved_multi_run_progress[k]["achievement_id"] < id:
            k += 1
        

        name = achievements[id].name
        entry = { "out_of": achievements[id].endgoal, "time_achieved": None }
        reached = 0

        if j < len(already_achieved) and already_achieved[j]["achievement_id"] == id:
            reached = achievements[id].endgoal
            entry["time_achieved"] = already_achieved[j]["time_achieved"]
            j += 1
        elif not achievements[id].is_multi_run_achievement:
            reached = 0
        elif k < len(unachieved_multi_run_progress) and unachieved_multi_run_progress[k]["achievement_id"] == id:
            reached = unachieved_multi_run_progress[k]["progress_as_number"]
            k += 1
        else:
            reached = 0
        
        entry["reached"] = reached
        all_achievements[name] = entry

    return all_achievements      


def main():

    config = json.load(open("config/default.json"))
    try:
        config.update(json.load(open("config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=config["DATABASE"]
    )

    achievements = {}

    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:

        add_all_achievements(cursor, achievements)

        # new_achievements = get_and_update_new_achievements(cursor, test_data_1, achievements)
        # for id in new_achievements:
        #     cursor.execute("SELECT name FROM list_of_achievements WHERE achievement_id = (%s)", (id, ))
        #     print(cursor.fetchone()["name"])


        # user = 3
        # all_achievements = get_all_achievements_and_progress(cursor, user, achievements)
        # print("user_id: ", user)
        # print(all_achievements)


        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
