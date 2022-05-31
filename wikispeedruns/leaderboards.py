from typing import Literal, Optional

import pymysql


# For local testing you can comment out this get_db import and use the below code to manually connect to the db
# and run the file directly. Preferabley, you should use unit tests (which I have yet to write)

from db import get_db
'''
import json

def get_db():
    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database="wikipedia_speedruns"
    )

    return conn
'''


# Get runs for a prompt, with lots of options (described below)
# See bottom of file for example usage
def get_leaderboard_runs(
    ########### identifies prompt ###########
    prompt_id: int,
    lobby_id: Optional[int] = None,

    run_id = None, # inlcude the current run

    ########### global filtering ###########
    show_unfinished: bool = False,
    show_anonymous: bool = False,

    user_id: int = None,

    # Whether the prompt was played before a number of minutes since release
    #   since active_start for daily prompts
    #   since create_date for lobby prompts (TODO not implemented)
    played_before: Optional[int] = None,

    # Whether a prompt was played after a certain number of minutes since now
    played_after: Optional[int] = None,

    ########### grouping behavior ###########

    # Which run for each user to use, >> IGNORED if user_id is given <<
    #   'all': don't choose, and just return all runs
    #   'first': return the first attempt, not necessarily finished
    #   'shortest': return the shortest (finished) path
    user_run_mode: Literal['all', 'first', 'shortest'] = 'first',

    ########### sorting behavior ###########

    # How to sort the data
    #   'time': play_time
    #   'length': path length
    #   'start': start_time
    sort_mode: Literal['time', 'length', 'start'] = 'time',
    sort_asc: bool = True,

    ########### pagination ###########
    offset: int = 0,
    limit: Optional[int] = 100,
):
    # conditions is a set of templated SQL expressions to include in the final WHERE clause
    # query_args are the user inputs that will be filled by cursor.execute
    query_args = {}
    conditions = []

    # Aliased as 'runs', 'prompts' respectively
    base_table = "sprint_runs" if lobby_id is None  else "lobby_runs"
    prompts_table = "sprint_prompts" if lobby_id is None  else "lobby_prompts"

    prompts_join = "prompts.prompt_id = runs.prompt_id"
    if (lobby_id):
        prompts_join += " AND prompts.lobby_id = runs.lobby_id"



    # Add prompt identification to conditions
    conditions.append("runs.prompt_id = %(prompt_id)s")
    query_args["prompt_id"] = prompt_id
    if lobby_id is not None:
        conditions.append("runs.lobby_id = %(lobby_id)s")
        query_args["lobby_id"] = lobby_id



    # Filter by user (i.e. to only show own runs)
    if user_id is not None:
        conditions.append("runs.user_id = %(user_id)s")
        query_args["user_id"] = user_id



    # Filter unfinished runs and anonymous (only in sprint_runs)
    if not show_unfinished:
        conditions.append('finished = 1')

    if lobby_id is None and not show_anonymous:
        conditions.append('runs.user_id IS NOT NULL')



    # Filter by time
    if played_before is not None:
        if lobby_id is not None:
            return NotImplementedError("played_before not implemneted for lobby_promts")
        else:
            conditions.append('runs.start_time <= DATE_ADD(prompts.active_start, INTERVAL %(played_before)s MINUTE)')
            query_args['played_before'] = played_before

    if played_after is not None:
        conditions.append('runs.start_time >= DATE_ADD(NOW(), INTERVAL -%(played_after)s MINUTE)')
        query_args['played_after'] = played_after



    # Grouping by user
    group_subquery = ""
    if user_id is None:
        # TODO warning otherwise?
        if user_run_mode == 'first':
            # TODO Note this relies on run_id being autoincrement, which is a bit ehh
            # We need to either always record start time or something when opening the prompt
            # TODO this also is a bit weird if user_id and name are both populated, check this
            group_subquery = f"""
                JOIN (
                    SELECT MIN(run_id) AS run_id
                    FROM {base_table}
                    WHERE prompt_id=%(prompt_id)s {"AND lobby_id=%(lobby_id)s" if base_table == "lobby_runs" else ""}
                    GROUP BY user_id {", name" if base_table == "lobby_runs" else ""}
                ) AS first_runs
                ON first_runs.run_id = runs.run_id
                """

        elif user_run_mode == 'shortest':
            group_subquery = f"""
                JOIN (
                    SELECT run_id, MAX(JSON_LENGTH(`path`, '$.path')) AS path_length
                    FROM {base_table}
                    WHERE prompt_id=%(prompt_id)s {"AND lobby_id=%(lobby_id)s" if base_table == "lobby_runs" else ""}
                    GROUP BY user_id {", name" if base_table == "lobby_runs" else ""}
                ) AS shortest_runs
                ON shortest_runs.run_id = runs.run_id
                """
        elif user_run_mode == 'all':
            group_subquery = ""
        else:
            raise ValueError(f"Invalid user_run_mode '{user_run_mode}'")



    # Sorting
    sort_exp = ''
    if (sort_mode == 'time'):
        sort_exp = 'play_time'
    elif (sort_mode == 'length'):
        sort_exp = 'path_length' # note this relies on the select aliasing a path_length column below
    elif (sort_mode == 'start'):
        sort_exp = 'start_time'
    else:
        raise ValueError(f"Invalid sort mode '{sort_mode}'")

    if not sort_asc:
        sort_exp += ' DESC'


    # Pagination
    limit_exp = 'LIMIT %(offset)s, %(limit)s' if limit is not None else ''
    query_args['offset'] = offset
    query_args['limit'] = limit


    # Specific Run
    current_run_clause = ''
    if run_id is not None:
        current_run_clause = 'OR runs.run_id = %(run_id)s'
        query_args['run_id'] = run_id


    # Some specifics
    assert(len(conditions) > 0)

    # TODO maybe dont' use * here and instead select specific columns?
    # TODO save path length elsewhere?
    query = f"""
    SELECT runs.*, users.username, JSON_LENGTH(runs.`path`, '$.path') AS path_length
    FROM {base_table} AS runs
    LEFT JOIN {prompts_table} AS prompts ON {prompts_join}
    LEFT JOIN users ON users.user_id=runs.user_id
    {group_subquery}
    WHERE ({' AND '.join(conditions)}) {current_run_clause}
    ORDER BY {sort_exp}
    {limit_exp}
    """

    db = get_db()
    with db.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        print(cursor.mogrify(query, query_args))
        cursor.execute(query, query_args)
        return cursor.fetchall()



'''
if __name__ == "__main__":

    # Example usage
    # Get normal leaderboard for prompt 22 (i.e. first playes within 24 hours of release)
    # Along with current run_results
    get_leaderboard_runs(prompt_id=22, run_id=1111, user_run_mode="all", sort_mode='length', played_before=24 * 60)

    # Get the 10 longest (finished) runs for prompt 22
    get_leaderboard_runs(prompt_id=22, user_run_mode="all", sort_mode='length', sort_asc=False, limit=10)

    # Get the most recent runs, included unfinished, for prompt 22, within 1 day
    get_leaderboard_runs(prompt_id=22, user_run_mode="all", sort_mode='start', sort_asc=False, limit=10, played_after=24 * 60)

    # Get normal leaderboard for prompt 1 of lobby 4
    get_leaderboard_runs(lobby_id=4, prompt_id=1)

    # Get shortest path leaderboard for prompt 1 of lobby 4
    get_leaderboard_runs(lobby_id=4, prompt_id=1, user_run_mode='shortest', sort_mode="length")

'''