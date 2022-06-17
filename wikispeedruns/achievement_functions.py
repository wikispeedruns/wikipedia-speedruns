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
2. Write an append_achievement() statement for place_all_achievements_in_list(), passing in data accordingly
"""


"""
TO REMOVE AN ACHIEVEMENT:
1. Remove the append_achievement() statement for the function
2. Make sure to run script to actually delete this achievement from database
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

def visit_45(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "45 (number)" in single_run_article_map, None, None

def visit_46(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "46 (number)" in single_run_article_map, None, None

def visit_food(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "food" in single_run_article_map, None, None

def visit_30(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "30 (number)" in single_run_article_map, None, None

def visit_45_twice(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "45 (number)" in single_run_article_map and single_run_article_map["45 (number)"] >= 2, None, None



"""Real Achievements"""

def meta(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Wikipedia" in single_run_article_map, None, None

def bathroom_break(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Bathroom" in single_run_article_map, None, None

def luck_of_the_irish(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Ireland" in single_run_article_map, None, None

def all_roads_lead_to_rome(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Rome" in single_run_article_map, None, None

def time_is_money(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Currency" in single_run_article_map, None, None

def jet_fuel_cant_melt_steel_beams(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Conspiracy theory" in single_run_article_map, None, None

def i_am_not_a_crook(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Richard Nixon" in single_run_article_map, None, None

def this_is_sparta(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Sparta" in single_run_article_map, None, None

def mufasa_would_be_proud(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Simba" in single_run_article_map, None, None

def how_bizarre(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "One-hit wonder" in single_run_article_map, None, None

def gateway_to_the_world(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "List of sovereign states" in single_run_article_map, None, None

def heart_of_darkness(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Leopold II of Belgium" in single_run_article_map, None, None

def the_birds_and_the_bees(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Intimate relationship" in single_run_article_map, None, None

def emissionsgate(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Volkswagen emissions scandal" in single_run_article_map, None, None

def taking_over_the_internet(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Love Nwantiti" in single_run_article_map, None, None

def you_lost(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return sum(i >= 2 for i in list(single_run_article_map.values())) > 0, None, None

def fastest_gun_alive(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    num_links = len(single_run_data["path"]) - 1
    time_in_seconds = single_run_data["play_time"]
    seconds_per_click = time_in_seconds / num_links
    return seconds_per_click < 10, None, None

def carthago_delenda_est(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Third Punic War" in single_run_article_map and "Cato the Elder" in single_run_article_map, None, None

def back_to_square_one(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    starting_article: str = single_run_data["path"][0]["article"]
    return single_run_article_map[starting_article] >= 2, None, None

def merseyside_derby(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "Liverpool F.C." in single_run_article_map and "Everton F.C." in single_run_article_map, None, None

def the_matrix_trilogy(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return "The Matrix (franchise)" in single_run_article_map and "Matrix (mathematics)" in single_run_article_map and "Toyota Matrix" in single_run_article_map, None, None

def are_you_still_watching(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    path = single_run_data["path"]
    achieved = False
    for i in range(len(path) - 1):
        time_spent = path[i+1]["timeReached"] - path[i]["timeReached"] - path[i+1]["loadTime"]
        if time_spent >= 3600:
            achieved = True
    return achieved, None, None

def avengers_assemble(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    article_set = {"Thor (Marvel Comics)", "Captain America", "Hulk", "Iron Man", "Black Widow (Marvel Comics)", "Hawkeye (Clint Barton)"}
    achieved = True
    for article in article_set:
        if article not in single_run_article_map:
            achieved = False
    return achieved, None, None

def high_roller(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    path = single_run_data["path"]
    achieved = False
    for i in range(len(path) - 1):
        if path[i]["article"] == "Las Vegas" and path[i+1]["article"] == "Gambling":
            achieved = True
    return achieved, None, None

def marathon(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return len(single_run_article_map) >= 50, None, None

def back_so_soon(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    count = 0
    for article_name in single_run_article_map:
        if article_name.startswith("Sack of Rome"):
            count += 1
    return count >= 3, None, None

def what_a_mouthful(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    max_len = 0
    for article_name in single_run_article_map:
        max_len = max(max_len, len(article_name))
    return max_len > 25, None, None

def lightning_round(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    return single_run_data["play_time"] < 15, None, None

def around_the_world_in_80_seconds(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    article_set = {"North America", "South America", "Asia", "Europe", "Africa", "Australia (continent)", "Antarctica"}
    path = single_run_data["path"]

    current_map: Dict[str, int] = {}
    shortest_time = float("inf")
    load_time_sum = 0.0
    i, j, n = 0, 0, len(path)

    while i < n:
        while j < n and len(current_map) < len(article_set):
            article = path[j]["article"]
            if article in article_set:
                if article in current_map:
                    current_map[article] += 1
                else:
                    current_map[article] = 1
            load_time_sum += path[j]["loadTime"]
            j += 1

        if len(current_map) == len(article_set):
            shortest_time = min(shortest_time, 
            path[j-1]["timeReached"] - path[i]["timeReached"] - load_time_sum + path[i]["loadTime"])
            # add load_time of the first article since it doesn't count in the time wasted for load_time
        else:
            break

        article = path[i]["article"]
        current_map[article] -= 1
        if current_map[article] == 0:
            del current_map[article]
    
    return shortest_time <= 80, None, None

        


"""
*** Multiple Run Achievements ***

General Process:
1. Make the updates needed for progress
2. Return achieved (Boolean, based on data in progress)  +  the progress itself  +  the progress as a number
"""


"""Test Achievements"""

def visit_45_25_times(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    if "45 (number)" in single_run_article_map:
        current_progress += single_run_article_map["45 (number)"]
    return current_progress >= 25, current_progress, current_progress


"""Real Achievements"""


def friends(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    name_set = {"Jennifer Aniston", "Courteney Cox", "Lisa Kudrow", "Matt LeBlanc", "Matthew Perry", "David Schwimmer"}
    for name in name_set:
        if name in single_run_article_map:
            current_progress[name] = True
    return len(current_progress) == 6, current_progress, len(current_progress)

def land_of_the_free_home_of_the_brave(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    if "United States" in single_run_article_map:
        current_progress += single_run_article_map["United States"]
    return current_progress >= 50, min(current_progress, 50), min(current_progress, 50)

def super_size_me(single_run_data: Dict[str, Any], single_run_article_map: Dict[str, int], current_progress: Any) -> ReturnType:
    if "McDonald's" in single_run_article_map:
        current_progress += single_run_article_map["McDonald's"]
    return current_progress >= 10, min(current_progress, 10), min(current_progress, 10)


"""
Returns a list of dictionaries
Each dictionary has some information corresponding to the values
1. "function": Callable function
2. "name": str
3. "is_multi_run_achievement": bool
4. "endgoal": int
5. "default_progress": str
"""

def append_achievement(all_achievements: List[Dict[str, Any]], name: str, function: AchievementFunction, is_multi_run_achievement: bool, endgoal: int = 1, default_progress: str = "0") -> None:
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

    # test achievements
    append_achievement(all_achievements, "visit_30", visit_30, False)
    append_achievement(all_achievements, "visit_45", visit_45, False)
    append_achievement(all_achievements, "visit_46", visit_46, False)
    append_achievement(all_achievements, "visit_food", visit_food, False)
    append_achievement(all_achievements, "visit_45_twice", visit_45_twice, False)
    append_achievement(all_achievements, "visit_45_25_times", visit_45_25_times, True, 25, "0")


    # real achievements
    append_achievement(all_achievements, "meta", meta, False)
    append_achievement(all_achievements, "bathroom_break", bathroom_break, False)
    append_achievement(all_achievements, "luck_of_the_irish", luck_of_the_irish, False)
    append_achievement(all_achievements, "all_roads_lead_to_rome", all_roads_lead_to_rome, False)
    append_achievement(all_achievements, "time_is_money", time_is_money, False)
    append_achievement(all_achievements, "heart_of_darkness", heart_of_darkness, False)
    append_achievement(all_achievements, "the_birds_and_the_bees", the_birds_and_the_bees, False)
    append_achievement(all_achievements, "emissionsgate", emissionsgate, False)
    append_achievement(all_achievements, "taking_over_the_internet", taking_over_the_internet, False)
    append_achievement(all_achievements, "jet_fuel_cant_melt_steel_beams", jet_fuel_cant_melt_steel_beams, False)
    append_achievement(all_achievements, "i_am_not_a_crook", i_am_not_a_crook, False)
    append_achievement(all_achievements, "this_is_sparta", this_is_sparta, False)
    append_achievement(all_achievements, "mufasa_would_be_proud", mufasa_would_be_proud, False)
    append_achievement(all_achievements, "how_bizarre", how_bizarre, False)
    append_achievement(all_achievements, "gateway_to_the_world", gateway_to_the_world, False)

    append_achievement(all_achievements, "you_lost", you_lost, False)
    append_achievement(all_achievements, "fastest_gun_alive", fastest_gun_alive, False)
    append_achievement(all_achievements, "carthago_delenda_est", carthago_delenda_est, False)
    append_achievement(all_achievements, "back_to_square_one", back_to_square_one, False)
    append_achievement(all_achievements, "merseyside_derby", merseyside_derby, False)
    append_achievement(all_achievements, "the_matrix_trilogy", the_matrix_trilogy, False)
    append_achievement(all_achievements, "are_you_still_watching", are_you_still_watching, False)
    append_achievement(all_achievements, "avengers_assemble", avengers_assemble, False)
    append_achievement(all_achievements, "high_roller", high_roller, False)
    append_achievement(all_achievements, "marathon", marathon, False)
    append_achievement(all_achievements, "back_so_soon", back_so_soon, False)
    append_achievement(all_achievements, "what_a_mouthful", what_a_mouthful, False)
    append_achievement(all_achievements, "lightning_round", lightning_round, False)
    append_achievement(all_achievements, "around_the_world_in_80_seconds", around_the_world_in_80_seconds, False)

    append_achievement(all_achievements, "friends", friends, True, 6, "{}")
    append_achievement(all_achievements, "land_of_the_free_home_of_the_brave", land_of_the_free_home_of_the_brave, True, 50, "0")
    append_achievement(all_achievements, "super_size_me", super_size_me, True, 10, "0")

    return all_achievements
