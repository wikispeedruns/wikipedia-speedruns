# TODO support finding results around a certain table

from typing import Literal, Optional

from db import get_db


def get_leaderboard_runs(
    ########### identifies prompt ###########
    prompt_id: int,
    lobby_id: Optional[int] = None,

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
    #   'start': sorted by the recency of the attempt (newer ones first)
    sort_mode: Literal['time', 'length', 'recent'] = 'time',
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
    conditions.append("prompt_id = %(prompt_id)s")
    query_args["prompt_id"] = prompt_id
    if lobby_id is not None:
        conditions.append("lobby_id = %(lobby_id)s")
        query_args["lobby_id"] = prompt_id



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
                    SELECT MIN(run_id) AS first_run
                    FROM {base_table}
                    WHERE prompt_id=%(prompt_id)s {"AND lobby_id=%(lobby_id)s" if base_table == "lobby_runs" else ""}
                    GROUP BY user_id {", name" if base_table == "lobby_runs" else ""}
                ) AS first_runs
                ON first_runs.run_id = runs.run_id
                """

        elif user_run_mode == 'shortest':
            group_subquery = f"""
                JOIN (
                    SELECT user_id, run_id, MIN(JSON_LENGTH(runs.`path`, '$.path')) AS path_length
                    FROM {base_table}
                    WHERE prompt_id=%(prompt_id)s {"AND lobby_id=%(lobby_id)s" if base_table == "lobby_runs" else ""}
                    GROUP BY user_id {", name" if base_table == "lobby_runs" else ""}
                ) AS first_runs
                ON first_runs.run_id = runs.run_id
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
    elif (sort_mode == 'recent'):
        sort_exp = 'start_time'
    else:
        raise ValueError(f"Invalid sort mode '{sort_mode}'")

    if not sort_asc:
        sort_exp += ' DESC'


    # Pagination
    limit_exp = 'LIMIT %(offset)s, %(limit)s' if limit is not None else ''
    query_args['offset'] = offset
    query_args['limit'] = limit


    # TODO maybe dont' use * here and instead select specific columns?
    # TODO save apth length elsewhere?
    query = f"""
    SELECT runs.*, users.username, JSON_LENGTH(runs.`path`, '$.path') AS path_length
    FROM {base_table} AS runs
    LEFT JOIN {prompts_table} AS prompts ON {prompts_join}
    LEFT JOIN users ON users.user_id=runs.user_id
    {group_subquery}
    WHERE {' AND '.join(conditions)}
    ORDER BY {sort_exp}
    {limit_exp}
    """

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, query_args)
        return cursor.fetchall()


if __name__ == "__main__":
    get_leaderboard_runs(prompt_id=20)