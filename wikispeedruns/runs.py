from flask import jsonify, request, Blueprint, session
from datetime import datetime
import json
from typing import List, Literal, Tuple, TypedDict, Optional

from db import get_db, get_db_version
from pymysql.cursors import DictCursor

from wikispeedruns import lobbys

class PathEntry(TypedDict):
    article: str
    timeReached: float
    loadTime: float

# TODO deal with anonymous runs
def check_sprint_run_ownership(run_id: int, session: dict) -> bool:
    user_id = session.get("user_id")
    query = "SELECT user_id FROM lobby_runs WHERE run_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (run_id, ))
        (run_user_id,) = cursor.fetchone()

    # Either the id matches, or the run is an anonymous one
    return run_user_id is None or user_id == run_user_id

def check_lobby_run_ownership(run_id: int, lobby_id: int, session: dict) -> bool:
    user_id = session.get("user_id")
    name = None
    if "lobbys" in session:
        name = session["lobbys"].get(str(lobby_id))

    query = "SELECT user_id, name FROM lobby_runs WHERE run_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (run_id, ))
        (run_user_id, run_name) = cursor.fetchone()

    return (user_id is not None and user_id == run_user_id) or (name is not None and name == run_name)

# Creating run
def _create_run(prompt_id, lobby_id=None, user_id=None, name=None):
    '''
    Creates a new run given a prompt (either prompt_id or (lobby_id, prompt_id) ).
    Returns the ID of the run created.
    '''

    query_args = {
        "prompt_id" : prompt_id,
        "start_time": datetime.now(),
    }


    if lobby_id is None:
        query = "INSERT INTO `sprint_runs` (`prompt_id`,`user_id`, `start_time`) \
                 VALUES (%(prompt_id)s, %(user_id)s, %(start_time)s);"

        query_args["user_id"] = user_id

    else:
        query = "INSERT INTO `lobby_runs` (`lobby_id`, `prompt_id`,  `user_id`, `start_time`, `name`) \
                 VALUES (%(lobby_id)s, %(prompt_id)s, %(user_id)s, %(start_time)s, %(name)s)"

        if (user_id is None and name is None):
            raise ValueError("'user_id' or 'name' should be defined for lobby prompt")

        query_args["lobby_id"] = lobby_id
        query_args["user_id"] = user_id
        query_args["name"] = name

    sel_query = "SELECT LAST_INSERT_ID()"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, query_args)
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

    return id


def create_lobby_run(prompt_id: int, lobby_id: int, user_id: Optional[int] = None, name: Optional[str] = None) -> int:
    return _create_run(prompt_id, lobby_id=lobby_id, user_id=user_id, name=name)

def create_sprint_run(prompt_id: int, user_id=Optional[int]) -> int:
    return _create_run(prompt_id=prompt_id, user_id=user_id, name=None)

def create_quick_run(prompt_start: str, prompt_end: str, language: str, user_id: Optional[int] = None) -> int:
    query_args = {
        "prompt_start": prompt_start,
        "prompt_end": prompt_end,
        "language": language,
        "user_id": user_id
    }

    query = "INSERT INTO `quick_runs` (`prompt_start`, `prompt_end`, `language`, `user_id`) \
        VALUES (%(prompt_start)s, %(prompt_end)s, %(language)s, %(user_id)s);"
    
    sel_query = "SELECT LAST_INSERT_ID()"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, query_args)
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()
        return id


# Updating runs
def _update_run(run_id: int, start_time: datetime, end_time: datetime,
                      path: List[PathEntry], finished: bool, run_type: str):
    pathStr = json.dumps({
        'version': get_db_version(),
        'path': path
    })

    duration = (end_time - start_time).total_seconds()
    total_load_time = sum([entry.get('loadTime') for entry in path[1:]]) + path[0].get('timeReached')
    play_time = duration - total_load_time

    # Fall-through case for https://github.com/wikispeedruns/wikipedia-speedruns/issues/395
    # We can remove the band-aid fix if we stop seeing negative times
    if (play_time < -5 and finished and not run_type != 'lobby'):
        path[0]['timeReached'] = 0
        new_total_load_time = sum([entry.get('loadTime') for entry in path[1:]]) + path[0].get('timeReached') 
        assert(duration >= new_total_load_time)

        # Try and submit finished run with fixed time
        _update_run(run_id, start_time, end_time, path, finished, run_type)

        # Still raise exception for original time 
        raise ValueError(f"Invalid play_time '{play_time}'")

    query_args = {
        "run_id": run_id,
        "start_time": start_time,
        "end_time": end_time,
        "play_time": play_time,
        "finished": finished,
        "path": pathStr
    }

    db = get_db()
    with db.cursor() as cursor:
        query = f'''
        UPDATE `{run_type}_runs`
        SET `start_time`=%(start_time)s, `end_time`=%(end_time)s, `play_time`=%(play_time)s, `finished`=%(finished)s, `path`=%(path)s
        WHERE `run_id`=%(run_id)s
        '''

        cursor.execute(query, query_args)
        db.commit()

    return run_id

def update_lobby_run(run_id: int, start_time: datetime, end_time: datetime,
                      path: List[PathEntry], finished: bool):
    return _update_run(run_id, start_time, end_time, path, finished, run_type='lobby')

def update_sprint_run(run_id: int, start_time: datetime, end_time: datetime,
                      path: List[PathEntry], finished: bool):
    return _update_run(run_id, start_time, end_time, path, finished, run_type='sprint')

def update_quick_run(run_id: int, start_time: datetime, end_time: datetime,
                      path: List[PathEntry], finished: bool):
    return _update_run(run_id, start_time, end_time, path, finished, run_type='quick')
