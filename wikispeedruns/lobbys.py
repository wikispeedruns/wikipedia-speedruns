from cProfile import run
from datetime import datetime
import json
from os import remove
from typing import List, Literal, Tuple, TypedDict, Optional
from unittest import result

import pymysql

from db import get_db, get_db_version
from pymysql.cursors import DictCursor

from wikispeedruns import runs

import secrets

class LobbyPrompt(TypedDict):
    prompt_id: int
    lobby_id: int
    start: str
    end: str

    played: bool

def _random_passcode() -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(6)])

def parse_session(lobby_id: int, session: dict) -> Optional[Tuple[str, str]]:
    '''
    Given session and lobby, returns the tuple (column name, value, is_owner)
    corresponding to the user's entries in the lobbys_run table
    '''
    user_id = session.get("user_id")
    user_info = get_lobby_user_info(lobby_id, user_id)

    if user_info is not None:
        return ("user_id", user_id, user_info["owner"])

    if "lobbys" in session and str(lobby_id) in session["lobbys"] is not None:
        return ("name", session["lobbys"][str(lobby_id)], False)

    return None


def check_membership(lobby_id: int, session: dict) -> bool:
    user_id = session.get("user_id")
    if get_lobby_user_info(lobby_id, user_id) is not None:
        return True

    # lobby_id gets converted to string in session when creating cookie apparently
    if "lobbys" in session and session["lobbys"].get(str(lobby_id)) is not None:
        return True

    return False


def check_user_membership(lobby_id: int, user_id: int) -> bool:
    if get_lobby_user_info(lobby_id, user_id) is not None:
        return True

    return False


def check_prompt_end_visibility(lobby_id: int, session: dict) -> bool:
    user_id = session.get("user_id")
    user_info = get_lobby_user_info(lobby_id, user_id)

    # Owner always needs to view prompts
    if user_info and user_info["owner"]:
        return True

    # Check lobby rules
    lobby = get_lobby(lobby_id)
    return not lobby["rules"].get("hide_prompt_end", False)


def check_leaderboard_access(lobby_id: int, prompt_id: int, session: dict) -> bool:
    user_id = session.get("user_id")

    lobby = get_lobby(lobby_id)

    # if lobby rules don't restrict leaderboard access
    if not lobby["rules"].get("restrict_leaderboard_access", False):
        return True

    user_info = get_lobby_user_info(lobby_id, user_id)
    # Owner can always view leaderboard
    if user_info and user_info["owner"]:
        return True

    played_query = "SELECT COUNT(*) as played FROM lobby_runs WHERE lobby_id=%s AND prompt_id=%s"
    # check to see if played by user/anon user
    if user_info is not None:
        played_query += " AND user_id=%s"
        args = (lobby_id, prompt_id, user_id)
    else:
        if "lobbys" not in session: return False
        name = session["lobbys"].get(str(lobby_id))
        if name is None: return False

        played_query += " AND name=%s"
        args = (lobby_id, prompt_id, name)

    with get_db().cursor(cursor=DictCursor) as cursor:
        print(cursor.mogrify(played_query, args))
        cursor.execute(played_query, args)
        res = cursor.fetchone()


    if res is not None:
        return res["played"] > 0

    return False


# TODO let non users also create lobbies?
def create_lobby(user_id: int,
                 rules: Optional[str]=None,
                 name: Optional[str]=None,
                 desc: Optional[str]=None) -> Optional[int]:
    lobby_query = """
    INSERT INTO lobbys (`name`, `desc`, passcode, create_date, active_date, rules)
    VALUES (%(name)s, %(desc)s, %(passcode)s, %(now)s, %(now)s, %(rules)s);
    """
    user_query = """
    INSERT INTO user_lobbys (user_id, lobby_id, `owner`)
    VALUES (%s, %s, 1);
    """

    passcode = _random_passcode()
    now = datetime.now()

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(lobby_query, {
            "name": name,
            "desc": desc,
            "passcode": passcode,
            "now": now,
            "rules": rules
        })

        cursor.execute("SELECT LAST_INSERT_ID()")
        lobby_id = cursor.fetchone()[0]

        cursor.execute(user_query, (user_id, lobby_id))
        db.commit()

        return lobby_id


def get_lobby(lobby_id: int) -> Optional[dict]:
    query = """
        SELECT lobby_id, `name`, `desc`, passcode, create_date, active_date, rules
        FROM lobbys
        WHERE lobby_id=%s
    """
    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (lobby_id,))
        lobby = cursor.fetchone()

        try:
            lobby["rules"] = json.loads(lobby.get("rules", "{}"))
        except TypeError:
            lobby["rules"] = {}

    return lobby



def update_lobby(lobby_id: int,
                 rules: Optional[str]=None,
                 name: Optional[str]=None,
                 desc: Optional[str]=None) -> Optional[int]:
    query = """
        UPDATE lobbys SET {}
        FROM lobbys
        WHERE lobby_id=%s
    """

    cols = []
    args = []

    if rules is not None:
        cols += "rules=%s"
        args += rules

    if name is not None:
        cols += "name=%s"
        args += name

    if desc is not None:
        cols += "desc=%s"
        args += desc

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query.format(",".join(cols)), args)
        db.commit()

    return True


# Lobby Prompt Management

def add_lobby_prompt(lobby_id: int, start: int, end: int, language: str) -> bool:
    query = """
    INSERT INTO lobby_prompts (lobby_id, start, end, language, prompt_id)
    SELECT %(lobby_id)s, %(start)s, %(end)s, %(language)s, IFNULL(MAX(prompt_id) + 1, 1)
    FROM lobby_prompts WHERE lobby_id=%(lobby_id)s;
    """

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, {
            "lobby_id": lobby_id,
            "start": start,
            "end": end,
            "language": language
        })
        db.commit()

        return True

# passing session here is a bit messy
def get_lobby_prompts(lobby_id: int, prompt_id: Optional[int]=None, session: Optional[dict]=None) -> List[LobbyPrompt]:
    ## TODO user_id?]

    query = f"SELECT prompt_id, start, end, language FROM lobby_prompts WHERE lobby_id=%(lobby_id)s {'AND prompt_id=%(prompt_id)s' if prompt_id else ''}"

    query_args = {
        "lobby_id": lobby_id
    }

    player = None if session is None else parse_session(lobby_id, session)
    if player is not None:
        # TODO handle prompt_id better
        query = f"""
        SELECT p.prompt_id, start, end, language, played FROM lobby_prompts AS p
        LEFT JOIN  (
            SELECT lobby_id, prompt_id, COUNT(*) AS played
            FROM lobby_runs
            WHERE
                {player[0]}=%(player_value)s
                AND lobby_id=%(lobby_id)s {"AND prompt_id=%(prompt_id)s" if prompt_id else ""}
            GROUP BY lobby_id, prompt_id
        ) r
        ON r.prompt_id = p.prompt_id AND r.lobby_id = p.lobby_id
        WHERE p.lobby_id=%(lobby_id)s {"AND p.prompt_id=%(prompt_id)s" if prompt_id else ""}
        """

        query_args["player_value"] = player[1]


    if (prompt_id):
        query_args["prompt_id"] = prompt_id

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, query_args)
        return cursor.fetchall()


def delete_lobby_prompts(lobby_id: int, prompts: List[int]) -> bool:
    tables = ['lobby_runs', 'lobby_prompts']

    query_start = 'DELETE FROM'
    query_body = 'WHERE lobby_id=%(lobby_id)s AND prompt_id IN %(prompts)s'

    query_args = {
        "lobby_id": lobby_id,
        "prompts": tuple(prompts)
    }

    db = get_db()
    with db.cursor() as cursor:
        for table in tables:
            query = f'{query_start} {table} {query_body}'
            cursor.execute(query, query_args)
        db.commit()

        return True

# Lobby user management

def join_lobby_as_user(lobby_id: int, user_id: int) -> bool:
    query = "INSERT INTO user_lobbys (lobby_id, user_id) VALUES (%s, %s)"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        try:
            cursor.execute(query, (lobby_id, user_id))
            db.commit()
        except pymysql.IntegrityError:
            # Lobby or user does not exist
            return False

    return True


def get_lobby_user_info(lobby_id: int, user_id: Optional[int]) -> Optional[dict]:
    query = "SELECT owner FROM user_lobbys WHERE lobby_id=%s AND user_id=%s"

    if (user_id == None): return None

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (lobby_id, user_id))
        return cursor.fetchone()


# Lobby Runs
def get_lobby_runs(lobby_id: int, prompt_id: Optional[int]=None):
    query = """
        SELECT run_id, prompt_id, users.username, name, start_time, end_time, play_time, finished, `path`
        FROM lobby_runs
        LEFT JOIN users ON users.user_id=lobby_runs.user_id
        WHERE lobby_id=%(lobby_id)s AND path IS NOT NULL AND finished IS TRUE
    """

    query_args = {
        "lobby_id": lobby_id
    }

    if (prompt_id):
        query += " AND prompt_id=%(prompt_id)s"
        query_args["prompt_id"] = prompt_id

    query += " ORDER BY play_time"

    db = get_db()

    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, query_args)
        results = cursor.fetchall()
        for run in results:
            run['path'] = json.loads(run['path'])['path']

        return results

def get_lobby_run(lobby_id: int, run_id: int):
    query = """
        SELECT run_id, prompt_id, users.username, name, start_time, end_time, play_time, `path`
        FROM lobby_runs
        LEFT JOIN users ON users.user_id=lobby_runs.user_id
        WHERE lobby_id=%(lobby_id)s AND run_id=%(run_id)s
    """

    query_args = {
        "lobby_id": lobby_id,
        "run_id": run_id
    }

    db = get_db()

    with db.cursor(cursor=DictCursor) as cursor:
        # print(cursor.mogrify(query, query_args))
        cursor.execute(query, query_args)
        results = cursor.fetchone()

        results['path'] = json.loads(results['path'])['path']
        return results



def get_user_lobbys(user_id: int):
    query = """
    SELECT
        lobbys.lobby_id,
        `name`,
        `desc`,
        passcode,
        create_date,
        active_date,
        rules,
        user_lobbys.owner,
        count(prompt_id) as n_prompts
    FROM lobbys
    LEFT JOIN user_lobbys ON user_lobbys.lobby_id=lobbys.lobby_id
    LEFT JOIN lobby_prompts ON lobby_prompts.lobby_id=lobbys.lobby_id
    WHERE user_id=%(user_id)s
    GROUP BY lobby_id, user_lobbys.owner;
    """

    query_args = {
        "user_id": user_id,
    }

    db = get_db()

    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, query_args)
        results = cursor.fetchall()
        return results


def change_lobby_host(lobby_id: int, target_user_id: int):
    remove_host_query = """
    UPDATE user_lobbys
    SET owner=0
    WHERE owner=1 AND lobby_id=%(lobby_id)s
    """

    set_host_query = """
    UPDATE user_lobbys
    SET owner=1
    WHERE user_id=%(target_user_id)s AND lobby_id=%(lobby_id)s
    """

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(remove_host_query, {
            "lobby_id": lobby_id,
        })

        cursor.execute(set_host_query, {
            "target_user_id": target_user_id,
            "lobby_id": lobby_id
        })
        db.commit()

        return True



def get_lobby_users(lobby_id: int):
    query = """
    SELECT DISTINCT users.username, users.user_id, owner FROM user_lobbys
    LEFT JOIN users ON user_lobbys.user_id = users.user_id
    WHERE lobby_id=%s
    """

    db = get_db()

    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (lobby_id,))
        results = cursor.fetchall()

        return results



def get_lobby_anon_users(lobby_id: int):
    query = """
    SELECT DISTINCT name FROM lobby_runs
    WHERE lobby_id=%s AND user_id IS NULL
    """

    db = get_db()

    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (lobby_id,))
        results = cursor.fetchall()

        return results