from datetime import datetime
from typing import List, Literal, Tuple, TypedDict, Optional

import pymysql

from db import get_db
from pymysql.cursors import DictCursor

import secrets

class LobbyPrompt(TypedDict):
    prompt_id: int
    lobby_id: int
    start: str
    end: str

def _random_passcode() -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(6)])


# TODO let non users also create lobbies?
def create_lobby(user_id: int,
                 rules: str=None,
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
        return cursor.fetchone()

# Lobby Prompt Management

def add_lobby_prompt(lobby_id: int, start: int, end: int) -> bool:
    query = """
    INSERT INTO lobby_prompts (lobby_id, start, end, prompt_id
    VALUES(
        %(lobby_id)s, %(start)s, %(end)s, (
            SELECT IFNULL(MAX(prompt_id) + 1, 1)
            FROM lobby_prompts
            WHERE lobby_id=%(lobby_id)s
        )
    );
    """

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, {
            "lobby_id": lobby_id,
            "start": start,
            "end": end
        })
        db.commit()

        return True


def get_lobby_prompts(lobby_id: int) -> List[LobbyPrompt]:
    query = "SELECT prompt_id, start, end FROM lobby_prompts WHERE lobby_id=%s"
    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, {
            "lobby_id": lobby_id,
        })
        db.commit()


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

# TODO scores, users