'''
Implementation of following rating algorithm
https://codeforces.com/blog/entry/20762
'''

import datetime
import pymysql
from pymysql.cursors import DictCursor

import itertools
import pprint

USER_QUERY = 'SELECT username from users'

RUNS_QUERY = ('''
SELECT runs.run_id, runs.prompt_id, users.user_id, users.username, MIN(runs.start_time) as start_time,
        TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
FROM runs 
LEFT JOIN users ON runs.user_id=users.user_id 
WHERE users.user_id IS NOT NULL
GROUP BY runs.user_id, runs.prompt_id
ORDER BY runs.prompt_id, run_time
''')

INITIAL_RATING = 1500

pp = pprint.PrettyPrinter(indent=4)

def elo_prob(ri, rj):
    return 1 / (1 + 10 ** ((rj - ri) / 400 ))

def calculate_seed(users, round):
    for u in round:
        users[u]["seed"] = 1
        for v in round:
            if (u == v): continue
            users[u]["seed"] += elo_prob(users[v]["rating"], users[u]["rating"])


def calculate_place(users, round):
    for place, u in enumerate(round):
        users[u]["place"] = (place + 1)

def calculate_desired_seed(users):
    for u in users:
        user = users[u]
        if ("seed" not in user or "place" not in user): continue

        user["desired_seed"] = (user["seed"] * user["place"]) ** 0.5

def rating_for_seed(users, round, u, desired_seed):
    lo = 1
    hi = 8000

    while (lo < hi):
        mid = (lo + hi) // 2

        mid_seed = 1

        # TODO should we exclude ourselves?
        for v in round:
            if (u == v): continue
            mid_seed += elo_prob(users[v]["rating"], mid)

        if (mid_seed > desired_seed):
            lo = mid + 1
        else:
            hi = mid

    return lo

def calculate_new_ratings(users, round):
    for u in round:
        users[u]["target"] = rating_for_seed(users, round, u, users[u]["desired_seed"])
    
    # if we change it in the loop above, it will affect things
    for u in round:
        users[u]["rating"] = (users[u]["target"] + users[u]["rating"]) // 2


def update(users, round):
    if (len(round) == 1): return

    calculate_seed(users, round)
    calculate_place(users, round)
    calculate_desired_seed(users)
    calculate_new_ratings(users, round)
    pp.pprint(users)

    # Erase temp. fields and add new rating
    users = {k: {"rating": v["rating"] }  for k, v in users.items()}

def main():
    conn = pymysql.connect(user='user', host='127.0.0.1', database='wikipedia_speedruns')

    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.execute(USER_QUERY)
        users = {u['username']: {"rating": INITIAL_RATING}  for u in cursor.fetchall()}

        cursor.execute(RUNS_QUERY)
        runs = cursor.fetchall()

    for k, round in itertools.groupby(runs, lambda r: r['prompt_id']):
        print(f"Processing Round {k}")
        round = [run["username"] for run in round]
        update(users, round)


if __name__ == "__main__":
    main()