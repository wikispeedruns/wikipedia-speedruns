from typing import Literal, Optional

import pymysql
import json


# For local testing you can comment out this get_db import and use the below code to manually connect to the db
# and run the file directly. Preferably, you should use unit tests (which I have yet to write)
from db import get_db
'''
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

    run_id = None, # include the current run

    ########### global filtering ###########
    show_unfinished: bool = False,
    show_anonymous: bool = False,

    # for personal leaderboards
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
    limit: Optional[int] = 20,

    # only return resulting query
    query_only: bool = False,
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
            return NotImplementedError("played_before not implemented for lobby_prompts")
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
                LEFT JOIN (
                    SELECT MIN(run_id) AS run_id
                    FROM {base_table}
                    WHERE prompt_id=%(prompt_id)s {"AND lobby_id=%(lobby_id)s" if base_table == "lobby_runs" else ""}
                    GROUP BY user_id {", name" if base_table == "lobby_runs" else ""}
                ) AS first_runs
                ON first_runs.run_id = runs.run_id
                """

            conditions.append("first_runs.run_id IS NOT NULL")

        elif user_run_mode == 'shortest':

            # This is gross so let me explain this
            # Basically, we want to figure out which (finished) run for a user is his shortest.
            #   - In terms of column, this is the MIN(finished, path_length)
            #   - Instead of grouping by user (+ name for lobbies), we use a window function to calculate
            #     the order of shortest path for all runs for each user
            #   - Then in the outer query we only select the first.
            # see https://stackoverflow.com/questions/7745609/sql-select-only-rows-with-max-value-on-a-column
            # and https://stackoverflow.com/questions/3800551/select-first-row-in-each-group-by-group
            group_subquery = f"""
                JOIN (
                    SELECT run_id,
                    ROW_NUMBER() OVER (PARTITION BY user_id {", `name`" if base_table == "lobby_runs" else ""}
                                    ORDER BY NOT finished, JSON_LENGTH({base_table}.`path`, '$.path')) AS shortest_path_rank
                    FROM {base_table}
                    WHERE prompt_id=%(prompt_id)s {"AND lobby_id=%(lobby_id)s" if base_table == "lobby_runs" else ""}
                ) AS grouped_runs
                ON grouped_runs.run_id = runs.run_id
                """
            conditions.append("grouped_runs.shortest_path_rank = 1")

        elif user_run_mode == 'all':
            group_subquery = ""
        else:
            raise ValueError(f"Invalid user_run_mode '{user_run_mode}'")



    # Sorting
    sort_exp = ''
    if (sort_mode == 'time'):
        sort_exp = 'play_time'
    elif (sort_mode == 'length'):
        sort_exp = "JSON_LENGTH(runs.`path`, '$.path'), play_time" # note this relies on the select aliasing a path_length column below
    elif (sort_mode == 'start'):
        sort_exp = 'start_time'
    else:
        raise ValueError(f"Invalid sort mode '{sort_mode}'")

    if not sort_asc:
        sort_exp += ' DESC'


    # Pagination, default 1 so all articles are chosen
    pagination_clause = '1'
    if limit is not None:
        pagination_clause = ("(`rank` BETWEEN %(page_start)s AND %(page_end)s)")
        query_args['page_start'] = offset + 1
        query_args['page_end'] = offset + limit


    # Current Run
    current_run_clause = '0'
    if run_id is not None:
        # TODO this is gross and hacky and relies on runs being the alias for both outer and
        # actual table
        current_run_clause = 'runs.run_id = %(run_id)s'
        query_args['run_id'] = run_id

    # Some specifics
    assert(len(conditions) > 0)

    # TODO maybe don't use * here and instead select specific columns?
    # TODO save path length elsewhere?
    # TODO query performance with row_number might not be great

    query = f"""
    SELECT runs.* FROM (
        SELECT
            runs.*,
            users.username,
            ROW_NUMBER() OVER (ORDER BY {sort_exp}) AS `rank`,
            COUNT(*) OVER () AS numRuns,
            JSON_LENGTH(runs.`path`, '$.path') AS path_length
        FROM {base_table} AS runs
        LEFT JOIN {prompts_table} AS prompts ON {prompts_join}
        LEFT JOIN users ON users.user_id=runs.user_id
        {group_subquery}
        WHERE ({' AND '.join(conditions)}) OR {current_run_clause}
        ORDER BY {sort_exp}
    ) AS runs
    WHERE {pagination_clause} OR {current_run_clause}
    ORDER BY {sort_exp}
    """

    if query_only:
        return { "query": query, "args": query_args }

    db = get_db()
    with db.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, query_args)

        results = cursor.fetchall()
        numRuns = 0
        for run in results:
            numRuns = run["numRuns"]
            del run['numRuns']

            # TODO temp fix
            if (run['path'] is None):
                run['path'] = []
            else:
                run['path'] = json.loads(run['path'])['path']

        return {
            "numRuns": numRuns,
            "runs": results
        }


'''
Leaderboard Stats
'''

def get_leaderboard_stats(
    prompt_id: int,
    lobby_id: Optional[int] = None,
    run_id: Optional[int] = None,
    **kwargs
): 
    lb_query = get_leaderboard_runs(prompt_id, lobby_id, run_id, limit=None, offset=0, query_only=True, **kwargs)

    query = f'''
    WITH data AS (
        {lb_query['query']}
    )

    SELECT
        COUNT(IF(finished, 1, NULL)) / COUNT(*) * 100 AS finish_pct,
        AVG(IF(finished, path_length, NULL)) AS avg_path_len,
        AVG(IF(finished, play_time, NULL)) AS avg_play_time
    FROM data
    '''
    
    db = get_db()
    with db.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, lb_query['args'])
        return cursor.fetchall()[0]

'''
if __name__ == "__main__":

    # Example usage
    # Get normal leaderboard for prompt 22 (i.e. first playes within 24 hours of release) along with current run_results
    runs = get_leaderboard_runs(prompt_id=22, run_id=1111, user_run_mode="all", sort_mode='length', played_before=24 * 60)

    # Get the 10 longest (finished) runs for prompt 22
    runs = get_leaderboard_runs(prompt_id=22, user_run_mode="all", sort_mode='length', sort_asc=False, limit=10)

    # Get the most recent runs, included unfinished, for prompt 22, within 1 day
    runs = get_leaderboard_runs(prompt_id=22, user_run_mode="all", sort_mode='start', sort_asc=False, limit=10, played_after=24 * 60)

    # Get normal leaderboard for prompt 1 of lobby 4
    runs = get_leaderboard_runs(lobby_id=4, prompt_id=1)

    # Get shortest path leaderboard for prompt 1 of lobby 4
    runs = get_leaderboard_runs(lobby_id=4, prompt_id=1, user_run_mode='shortest', sort_mode="length")

    # print([(run["rank"], run["run_id"]) for run in runs])
'''