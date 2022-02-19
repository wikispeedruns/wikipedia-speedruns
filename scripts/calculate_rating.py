'''
Implementation of following rating algorithm
https://codeforces.com/blog/entry/20762
'''

import datetime
import pymysql
import json
from pymysql.cursors import DictCursor

import itertools
import pprint

USER_QUERY = 'SELECT user_id, username from users'

# TODO technically if a user has the same start time, they'll show up twice, this could be an issue
RUNS_QUERY = ('''
SELECT runs.run_id, runs.prompt_id, runs.user_id, users.username,
        TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
FROM sprint_runs AS runs 
INNER JOIN daily_prompts AS d ON d.prompt_id=runs.prompt_id
RIGHT JOIN users ON runs.user_id=users.user_id 
INNER JOIN (
    SELECT user_id, MIN(start_time) as start_time
    FROM sprint_runs AS runs
    GROUP BY runs.prompt_id, runs.user_id
) t ON runs.user_id = t.user_id AND runs.start_time = t.start_time
WHERE d.rated = 1 AND runs.end_time IS NOT NULL AND d.date < CURDATE()
ORDER BY runs.prompt_id, run_time;
''')

STORE_RATINGS_QUERY = (
'''
REPLACE INTO ratings (user_id, rating, num_rounds) VALUES (%s, %s, %s);
'''
)

INITIAL_RATING = 1500

pp = pprint.PrettyPrinter(indent=4)

def _elo_prob(ri, rj):
    return 1 / (1 + 10 ** ((rj - ri) / 400 ))

def _calculate_seed(users, round):
    for u in round:
        users[u]["seed"] = 1
        for v in round:
            if (u == v): continue
            users[u]["seed"] += _elo_prob(users[v]["rating"], users[u]["rating"])


def _calculate_place(users, round):
    for place, u in enumerate(round):
        users[u]["place"] = (place + 1)

def _calculate_desired_seed(users):
    for u in users:
        user = users[u]
        if ("seed" not in user or "place" not in user): continue

        user["desired_seed"] = (user["seed"] * user["place"]) ** 0.5

def _rating_for_seed(users, round, u, desired_seed):
    lo = 1
    hi = 8000

    while (lo < hi):
        mid = (lo + hi) // 2

        mid_seed = 1

        # TODO should we exclude ourselves?
        for v in round:
            if (u == v): continue
            mid_seed += _elo_prob(users[v]["rating"], mid)

        if (mid_seed > desired_seed):
            lo = mid + 1
        else:
            hi = mid

    return lo


def _calculate_new_ratings(users, round):
    for u in round:
        users[u]["target"] = _rating_for_seed(users, round, u, users[u]["desired_seed"])
    
    # if we change it in the loop above, it will affect things
    for u in round:
        users[u]["rating"] = (users[u]["target"] + users[u]["rating"]) // 2


def _update(users, round):
    if (len(round) == 1): return

    for u in round: users[u]["num_rounds"] += 1

    _calculate_seed(users, round)
    _calculate_place(users, round)
    _calculate_desired_seed(users)
    _calculate_new_ratings(users, round)

def calculate_ratings():
    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"], 
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=config['DATABASE']
    )

    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.execute(USER_QUERY)
        
        users = {
            u['user_id']: {
                "rating": INITIAL_RATING, 
                "num_rounds": 0, 
                "username": u["username"]
            } for u in cursor.fetchall()
        }

        cursor.execute(RUNS_QUERY)
        runs = cursor.fetchall()

        # Assert to catch case where RUNS_QUERY has duplicates
        assert(len(runs) == len(set((r["prompt_id"], r["user_id"]) for r in runs)))

    for k, round in itertools.groupby(runs, lambda r: r['prompt_id']):
        print(f"Processing Round {k}")

        # Only take the first run for each
        round = [run["user_id"] for run in round]        
        _update(users, round)

    ratings = sorted([(v["rating"], v["num_rounds"], v["username"]) for k, v in users.items()])
    for (rating, num_rounds, username) in ratings:
        print(f"{username}: {rating} ({num_rounds})")

    # Update database
    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.executemany(STORE_RATINGS_QUERY, [(k, v["rating"], v["num_rounds"]) for k, v in users.items()])
        conn.commit()

if __name__ == "__main__":
    calculate_ratings()