'''
Implementation of following rating algorithm
https://codeforces.com/blog/entry/20762
'''

import itertools
import json
import pymysql

from pymysql.cursors import DictCursor


USER_QUERY = 'SELECT user_id, username from users'

# TODO technically if a user has the same start time, they'll show up twice, this could be an issue
RUNS_QUERY = ('''
SELECT r.run_id, r.prompt_id, r.user_id, u.username,
        TIMESTAMPDIFF(MICROSECOND, r.start_time, r.end_time) AS run_time
FROM sprint_runs AS r
INNER JOIN sprint_prompts AS p ON p.prompt_id=r.prompt_id
RIGHT JOIN users AS u ON r.user_id=u.user_id
INNER JOIN (
    SELECT user_id, MIN(run_id) as run_id
    FROM sprint_runs AS runs
    GROUP BY runs.prompt_id, runs.user_id
) t ON r.user_id = t.user_id AND r.run_id = t.run_id
WHERE p.rated = 1 AND r.end_time IS NOT NULL AND p.used AND p.active_end <= NOW()
ORDER BY p.active_start, run_time;
''')

STORE_RATINGS_QUERY = (
'''
REPLACE INTO ratings (user_id, rating, num_rounds) VALUES (%s, %s, %s);
'''
)

STORE_HISTORICAL_RATINGS_QUERY = (
'''
REPLACE INTO historical_ratings (user_id, prompt_id, prompt_date, `prompt_rank`, rating) VALUES
(
    %(user_id)s,
    %(prompt_id)s,
    (SELECT active_start FROM sprint_prompts where prompt_id=%(prompt_id)s),
    %(rank)s,
    %(rating)s
);
'''
)


INITIAL_RATING = 1500

def _elo_prob(ri, rj):
    return 1 / (1 + 10 ** ((rj - ri) / 400 ))

def _calculate_seed(users, round):
    for u in round:
        users[u]["seed"] = 1
        for v in round:
            if u == v: continue
            users[u]["seed"] += _elo_prob(users[v]["rating"], users[u]["rating"])


def _calculate_place(users, round):
    for place, u in enumerate(round):
        users[u]["place"] = (place + 1)

def _calculate_desired_seed(users):
    for u in users:
        user = users[u]
        if "seed" not in user or "place" not in user: continue

        user["desired_seed"] = (user["seed"] * user["place"]) ** 0.5

def _rating_for_seed(users, round, u, desired_seed):
    lo = 1
    hi = 8000

    while lo < hi:
        mid = (lo + hi) // 2

        mid_seed = 1

        # TODO should we exclude ourselves?
        for v in round:
            if u == v: continue
            mid_seed += _elo_prob(users[v]["rating"], mid)

        if mid_seed > desired_seed:
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
    if len(round) == 1: return

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

    for prompt_id, round in itertools.groupby(runs, lambda r: r['prompt_id']):
        print(f"Processing Prompt {prompt_id}")

        # Since we order by run time in our query, this is in order of ranking
        round = [run["user_id"] for run in round]
        _update(users, round)

        # Store historical data
        with conn.cursor(cursor=DictCursor) as cursor:
            cursor.executemany(STORE_HISTORICAL_RATINGS_QUERY,
                [
                    {
                        "user_id": user_id,
                        "prompt_id": prompt_id,
                        "rank": i + 1,
                        "rating": users[user_id]["rating"],
                    }
                    for i, user_id in enumerate(round)
                ]
            )
            conn.commit()


    # Store current ratings
    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.executemany(STORE_RATINGS_QUERY,
            [
                (k, v["rating"], v["num_rounds"])
                for k, v in users.items()
            ]
        )
        conn.commit()


    ratings = sorted([(v["rating"], v["num_rounds"], v["username"]) for k, v in users.items()])
    for (rating, num_rounds, username) in ratings:
        print(f"{username}: {rating} ({num_rounds})")


if __name__ == "__main__":
    calculate_ratings()