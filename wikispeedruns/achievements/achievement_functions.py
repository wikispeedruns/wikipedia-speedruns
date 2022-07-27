from typing import Tuple, Dict, Any, Optional, Callable, List
import json


ReturnType = Tuple[bool, Any, Optional[int]]
AchievementFunction = Callable[[Dict[str, Any], Dict[str, int], str], ReturnType]


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

    # only contains the required articles
    current_map: Dict[str, int] = {}
    shortest_time = float("inf")
    load_time_sum = 0.0
    i, j, n = 0, 0, len(path)

    # Sliding Window Algorithm
    # for each left index (i), finds the leftmost right index (j) that contains all required articles and considers it
    # If we move the left index forward (e.g. shrink the window), the right index can either stay the same or move forward
    # it can never shrink to the left

    while i < n:

        # moves the right pointer forward until all articles are contained or there are no articles left
        while j < n and len(current_map) < len(article_set):
            article = path[j]["article"]
            if article in article_set:
                if article in current_map:
                    current_map[article] += 1
                else:
                    current_map[article] = 1
            load_time_sum += path[j]["loadTime"]
            j += 1

        # all articles are contained in this window
        if len(current_map) == len(article_set):
            # subtracts out the loadTime, adds the first one since it doesn't actually count
            shortest_time = min(shortest_time,
            path[j-1]["timeReached"] - path[i]["timeReached"] - load_time_sum + path[i]["loadTime"])
        else:
            break

        # move the left pointer forward for next iteration
        article = path[i]["article"]
        i += 1

        if article in article_set:
            current_map[article] -= 1
            if current_map[article] == 0:
                del current_map[article]

    return shortest_time <= 80, None, None



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




def append_achievement(all_achievements: List[Dict[str, Any]], name: str, function: AchievementFunction,
is_multi_run_achievement: bool, is_time_dependent: bool, endgoal: int = 1, default_progress: str = "0") -> None:
    entry = {
        "name" : name,
        "function" : function,
        "is_multi_run_achievement" : is_multi_run_achievement,
        "is_time_dependent": is_time_dependent,
        "endgoal" : endgoal,
        "default_progress" : default_progress
    }
    all_achievements.append(entry)



def place_all_achievements_in_list() -> List[Dict[str, Any]]:

    all_achievements: List[Dict[str, Any]] = []

    append_achievement(all_achievements, "meta", meta, False, False)
    append_achievement(all_achievements, "bathroom", bathroom_break, False, False)
    append_achievement(all_achievements, "ireland", luck_of_the_irish, False, False)
    append_achievement(all_achievements, "rome", all_roads_lead_to_rome, False, False)
    append_achievement(all_achievements, "currency", time_is_money, False, False)
    append_achievement(all_achievements, "heart_of_darkness", heart_of_darkness, False, False)
    append_achievement(all_achievements, "birds_and_bees", the_birds_and_the_bees, False, False)
    append_achievement(all_achievements, "emissionsgate", emissionsgate, False, False)
    append_achievement(all_achievements, "love_nwantiti", taking_over_the_internet, False, False)
    append_achievement(all_achievements, "conspiracy_theory", jet_fuel_cant_melt_steel_beams, False, False)
    append_achievement(all_achievements, "richard_nixon", i_am_not_a_crook, False, False)
    append_achievement(all_achievements, "sparta", this_is_sparta, False, False)
    append_achievement(all_achievements, "simba", mufasa_would_be_proud, False, False)
    append_achievement(all_achievements, "how_bizarre", how_bizarre, False, False)
    append_achievement(all_achievements, "gateway_to_the_world", gateway_to_the_world, False, False)

    append_achievement(all_achievements, "you_lost", you_lost, False, False)
    append_achievement(all_achievements, "fastest_gun_alive", fastest_gun_alive, False, True)
    append_achievement(all_achievements, "carthago_delenda_est", carthago_delenda_est, False, False)
    append_achievement(all_achievements, "square_one", back_to_square_one, False, False)
    append_achievement(all_achievements, "merseyside_derby", merseyside_derby, False, False)
    append_achievement(all_achievements, "matrix", the_matrix_trilogy, False, False)
    append_achievement(all_achievements, "are_you_still_watching", are_you_still_watching, False, True)
    append_achievement(all_achievements, "avengers", avengers_assemble, False, False)
    append_achievement(all_achievements, "high_roller", high_roller, False, False)
    append_achievement(all_achievements, "marathon", marathon, False, False)
    append_achievement(all_achievements, "back_so_soon", back_so_soon, False, False)
    append_achievement(all_achievements, "mouthful", what_a_mouthful, False, False)
    append_achievement(all_achievements, "lightning_round", lightning_round, False, True)
    append_achievement(all_achievements, "around_the_world", around_the_world_in_80_seconds, False, True)

    append_achievement(all_achievements, "friends", friends, True, False, 6, "{}")
    append_achievement(all_achievements, "usa", land_of_the_free_home_of_the_brave, True, False, 50, "0")
    append_achievement(all_achievements, "mcdonalds", super_size_me, True, False, 10, "0")

    return all_achievements
