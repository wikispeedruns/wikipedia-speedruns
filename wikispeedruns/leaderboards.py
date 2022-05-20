# TODO support finding results around a certain table

from typing import Literal

def get_leaderboard_runs(
    ########### identifies prompt ###########
    prompt_id: int,
    lobby_id: int = None,

    ########### global filtering ###########
    show_unfinished: bool = False,
    show_anonymous: bool = False,

    # Whether the prompt was played before a number of minutes since release
    #   since active_start for daily prompts
    #   since create_date for lobby prompts (TODO not implmented)
    played_before: None = False,

    # Whether a prompt was played after a certain number of minutes since now
    played_after: None = False,

    ########### grouping behavior ###########

    # Which run for each user to use
    #   'all': don't choose, and just return all runs
    #   'first': return the first attempt
    #   'shortest': return the shortest path
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
    limit: int = 100,

):
    pass