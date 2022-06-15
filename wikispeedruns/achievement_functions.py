from typing import Tuple, Dict, Any, Optional, Callable, List
import json

test_data = {
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



"""
TO ADD AN ACHIEVEMENT:
1. Write its function satisfying the constraints below
2. Write an append statement in place_all_achievements_in_list, passing in data accordingly
"""


"""
*** Achievement Functions ***

Takes in 3 arguments:
1. single_run_data: data just like specified above in test_data
2. single_run_article_map: a dictionary mapping {article_name : times_visited}
3. current_progress (only useful in multi-run achievements): a JSON String storing data structure to be updated

Returns 3 values:
1. achieved (Boolean): Whether this achievement will be achieved after current run
2. progress (Some Data Structure): The progress on the current achievement after update; only useful for multiple run achievements
3. progress_as_number: The progress as a number out of some total value
"""

ReturnType = Tuple[bool, Any, Optional[int]]
AchievementFunction = Callable[[Dict[str, Any], Dict[str, int], str], ReturnType]


"""
*** Single Run Achievements ***
"""


"""Test Achievements"""

def visit_45(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "45 (number)" in single_run_article_map, None, None

def visit_46(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "46 (number)" in single_run_article_map, None, None

def visit_food(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "food" in single_run_article_map, None, None

def visit_45_twice(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "45 (number)" in single_run_article_map and single_run_article_map["45 (number)"] >= 2, None, None



"""Real Achievements"""

def meta(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Wikipedia" in single_run_article_map, None, None

def bathroom_break(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Bathroom" in single_run_article_map, None, None

def luck_of_the_irish(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Ireland" in single_run_article_map, None, None

def all_roads_lead_to_rome(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Rome" in single_run_article_map, None, None

def time_is_money(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Currency" in single_run_article_map, None, None

def jet_fuel_cant_melt_steel_beams(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Conspiracy theory" in single_run_article_map, None, None

def i_am_not_a_crook(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Richard Nixon" in single_run_article_map, None, None

def this_is_sparta(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Sparta" in single_run_article_map, None, None

def mufasa_would_be_proud(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Simba" in single_run_article_map, None, None

def how_bizarre(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "One-hit wonder" in single_run_article_map, None, None

def gateway_to_the_world(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "List of sovereign states" in single_run_article_map, None, None

def heart_of_darkness(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Leopold II of Belgium" in single_run_article_map, None, None

def the_birds_and_the_bees(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Intimate relationship" in single_run_article_map, None, None

def emissionsgate(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Volkswagen emissions scandal" in single_run_article_map, None, None

def taking_over_the_internet(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return "Love Nwantiti" in single_run_article_map, None, None

def you_lost(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    return sum(i >= 2 for i in list(single_run_article_map.values())) > 0, None, None






"""
*** Multiple Run Achievements ***

General Process:
1. load the JSON String current_progress into new_progress as data structure
2. Make the updates needed for progress
3. Return achieved (Boolean, based on data in progress)  +  the progress itself  +  the progress as a number
"""


"""Test Achievements"""

def visit_45_25_times(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    new_progress = json.loads(current_progress)
    new_progress += "45 (number)" in single_run_article_map
    return new_progress >= 25, new_progress, new_progress


"""Real Achievements"""

def friends(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: str) -> ReturnType:
    new_progress = json.loads(current_progress)
    name_set = {"Jennifer Aniston", "Courteney Cox", "Lisa Kudrow", "Matt LeBlanc", "Matthew Perry", "David Schwimmer"}
    for name in name_set:
        if name in single_run_article_map:
            new_progress[name] = True
    return len(new_progress) == 6, new_progress, len(new_progress)




"""
Returns a list of dictionaries
Each dictionary has some information corresponding to the values
1. "function": Callable function
2. "name": str
3. "is_multi_run_achievement": bool
4. "endgoal": int
5. "default_progress": str
"""

def append_achievement(all_achievements: List[Dict[str, Any]], name: str, function: AchievementFunction, is_multi_run_achievement: bool, endgoal: Optional[int] = 1, default_progress: Optional[str] = None) -> None:
    entry = {
        "name" : name,
        "function" : function,
        "is_multi_run_achievement" : is_multi_run_achievement,
        "endgoal" : endgoal,
        "default_progress" : default_progress
    }
    all_achievements.append(entry)

def place_all_achievements_in_list() -> List[Dict[str, Any]]:
    
    all_achievements: List[Dict[str, Any]] = []

    # add in all achievements desired into the list
    append_achievement(all_achievements, "visit_45", visit_45, False, 1, "")
    append_achievement(all_achievements, "visit_46", visit_46, False, 1, "")
    append_achievement(all_achievements, "visit_food", visit_food, False, 1, "")
    append_achievement(all_achievements, "visit_45_twice", visit_45_twice, False, 1, "")
    append_achievement(all_achievements, "you_lost", you_lost, False, 1, "")
    append_achievement(all_achievements, "visit_45_25_times", visit_45_25_times, True, 25, "0")
    append_achievement(all_achievements, "friends", friends, True, 6, "{}")

    return all_achievements
