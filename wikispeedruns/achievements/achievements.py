from ast import Return
from typing import List, Tuple, Dict, Any, Optional, Callable

import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from .achievement_functions import place_all_achievements_in_list

import pymysql
from pymysql.cursors import DictCursor

import json


def version_2_1(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    path = json.loads(raw_data["path"])
    actual_data = dict.copy(raw_data)
    actual_data["path"] = path["path"]
    actual_data["version"] = path["version"]
    return actual_data

def get_version_map():
    return {
        "1.0": version_2_1,
        "2.0": version_2_1,
        "2.1": version_2_1,
        "2.2": version_2_1
    }

def convert_to_standard(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    version_map = get_version_map()
    path = json.loads(raw_data["path"])
    version = path["version"]
    version_func = version_map[version] if version in version_map else version_2_1
    return version_func(raw_data)

def check_data(raw_data: Dict[str, Any]) -> bool:
    return raw_data["finished"] and raw_data["user_id"]


ReturnType = Tuple[bool, Any, Optional[int]]
AchievementFunction = Callable[[Dict[str, Any], Dict[str, int], str], ReturnType]


"""
*** Achievement Class ***
"""
class Achievement():

    EMPTY_RETURN_TYPE: ReturnType = (False, None, None)

    def __init__(self, name: str, function: AchievementFunction, is_multi_run_achievement: bool, is_time_dependent: bool,
    endgoal: int, default_progress: str) -> None:
        self.name = name
        self.check_function = function
        self.is_multi_run_achievement = is_multi_run_achievement
        self.is_time_dependent = is_time_dependent
        self.endgoal = endgoal
        self.default_progress = default_progress

    @staticmethod
    def no_time_data(single_run_data: Dict[str, Any]) -> bool:
        return single_run_data["version"] == "1.0"

    def check_status(self, single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> Tuple[bool, ReturnType]:
        if current_progress == "":
            current_progress = self.default_progress
        progress = json.loads(current_progress)

        if self.is_time_dependent and self.no_time_data(single_run_data):
            return False, self.EMPTY_RETURN_TYPE
        else:
            return True, self.check_function(single_run_data, single_run_article_map, progress)


"""
Returns achievements dictionary for achievement information
"""
def get_achievements_info(cursor: DictCursor) -> Dict[int, Achievement]:
    list_of_achievements = place_all_achievements_in_list()
    achievements: Dict[int, Achievement] = {}
    for achievement in list_of_achievements:
        num_rows = cursor.execute("SELECT achievement_id FROM list_of_achievements WHERE name = (%s)", (achievement["name"], ))
        if num_rows == 0:
            raise Exception("Achievement not present in database; make sure to add all achievements")
        achievement_id = cursor.fetchone()["achievement_id"]

        achievements[achievement_id] = Achievement(achievement["name"], achievement["function"],
        achievement["is_multi_run_achievement"], achievement["is_time_dependent"], achievement["endgoal"],
        achievement["default_progress"])
    return achievements


"""
Adds all the achievements present in the achievement_functions
"""
def add_all_achievements(cursor: DictCursor) -> None:
    list_of_achievements = place_all_achievements_in_list()
    for achievement in list_of_achievements:
        name = achievement["name"]
        num_rows = cursor.execute("SELECT achievement_id FROM list_of_achievements WHERE name = (%s)", (name, ))
        if num_rows == 0:
            cursor.execute("INSERT INTO list_of_achievements (name) VALUES (%s)", (name, ))


"""
returns all the new_achievements by the user after new run (using get_new_achievements)
and makes updates to database accordingly
"""
def get_and_update_new_achievements(cursor: DictCursor, raw_run_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    single_run_data = convert_to_standard(raw_run_data)

    achievements = get_achievements_info(cursor)
    new_achievements = get_new_achievements(cursor, single_run_data, achievements)

    return new_achievements


"""
returns all the new_achievements by the user after new run
"""
def get_new_achievements(cursor: DictCursor, single_run_data: Dict[str, Any], achievements: Dict[int, Achievement]) -> Dict[str, Dict[str, Any]]:

    # Create single_run_article_map as defined above
    single_run_article_map: Dict[str, int] = {}
    for entry in single_run_data["path"]:
        article = entry["article"]
        if article in single_run_article_map:
            single_run_article_map[article] += 1
        else:
            single_run_article_map[article] = 1


    new_achievements = {}
    user_id = single_run_data["user_id"]
    end_time = single_run_data["end_time"]

    achievements_progress = get_all_progress(cursor, user_id)
    j = 0

    for achievement_id in sorted(achievements):

        while j < len(achievements_progress) and achievements_progress[j]["achievement_id"] < achievement_id:
            j += 1

        present_in_database = j < len(achievements_progress) and achievements_progress[j]["achievement_id"] == achievement_id
        if present_in_database and achievements_progress[j]["achieved"]:
            continue

        current_progress = ""
        if present_in_database:
            current_progress = achievements_progress[j]["progress"]

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

        if present_in_database:
            achievements_progress[j]["progress"] = new_progress_as_string
            achievements_progress[j]["progress_as_number"] = new_progress_as_number
            achievements_progress[j]["achieved"] = achieved

        elif new_progress_as_string != achievements[achievement_id].default_progress:
            achievements_progress.append(
                {
                "achievement_id": achievement_id,
                "user_id": user_id,
                "progress": new_progress_as_string,
                "progress_as_number": new_progress_as_number,
                "achieved": achieved,
                }
            )

        if achieved:
            name = achievements[achievement_id].name
            new_achievements[name] = {
                "achieved": achieved,
                "time_reached": end_time,
                "reached": new_progress_as_number,
                "out of": achievements[achievement_id].endgoal
            }


    # Updates the achievements_progress table with the new progress data
    query = """
    INSERT INTO achievements_progress (achievement_id, user_id, progress, progress_as_number, achieved)
    VALUES (%(achievement_id)s, %(user_id)s, %(progress)s, %(progress_as_number)s, %(achieved)s)
    ON DUPLICATE KEY UPDATE progress = VALUES(progress), progress_as_number = VALUES(progress_as_number), achieved = VALUES(achieved)
    """
    cursor.executemany(query, achievements_progress)

    query = """
    UPDATE achievements_progress
    SET time_achieved = (%s)
    WHERE achieved = 1 AND time_achieved IS NULL
    """
    cursor.execute(query, (end_time, ))

    query = """
    UPDATE sprint_runs
    SET counted_for_am = 1 WHERE run_id = (%s)
    """
    cursor.execute(query, (single_run_data["run_id"]))

    return new_achievements



def get_all_progress(cursor: DictCursor, user_id: int) -> List[Dict[str, Any]]:
    query = """
    SELECT * FROM achievements_progress
    WHERE user_id = (%s)
    ORDER BY achievement_id
    """
    cursor.execute(query, (user_id,))
    return list(cursor.fetchall())


def get_all_achievements_and_progress(cursor: DictCursor, user_id: int) -> Dict[str, Dict[str, Any]]:

    achievements = get_achievements_info(cursor)
    achievements_progress = get_all_progress(cursor, user_id)
    j = 0
    all_achievements = {}

    for achievement_id in sorted(achievements):

        while j < len(achievements_progress) and achievements_progress[j]["achievement_id"] < achievement_id:
            j += 1

        name = achievements[achievement_id].name
        entry = { "out_of": achievements[achievement_id].endgoal }

        reached = 0
        time_reached = None
        achieved = 0

        present = j < len(achievements_progress) and achievements_progress[j]["achievement_id"] == achievement_id
        if present:
            reached = achievements_progress[j]["progress_as_number"]
            time_reached = achievements_progress[j]["time_achieved"]
            achieved = achievements_progress[j]["achieved"]
        else:
            reached = 0
            time_reached = None
            achieved = 0

        entry["reached"] = reached
        entry["time_reached"] = time_reached
        entry["achieved"] = achieved
        all_achievements[name] = entry

    return all_achievements
