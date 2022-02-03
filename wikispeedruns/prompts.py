
from typing import List, Literal, TypedDict, Optional

from db import get_db

from pymysql.cursors import DictCursor

import datetime

# TODO account for marathon prompts here


PromptType = Literal["marathon", "sprint"]


class Prompt(TypedDict):
    prompt_id: int
    start: str
    active_start: datetime.datetime
    active_end: datetime.datetime
    # played: bool # TODO

class SprintPrompt(Prompt):
    start: str
    end: Optional[str]

    currentlyRated: bool


class MarathonPrompt(Prompt):
    prompt_id: int
    start: str

    # TODO


def add_sprint_prompt(start: str, end: str) -> Optional[int]:
    ''' 
    Add a prompt
    '''
    query = "INSERT INTO prompts (start, end) VALUES (%s, %s);"
    sel_query = "SELECT LAST_INSERT_ID()"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (start, end))
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()
        return id


def set_ranked_daily_prompt(prompt_id: int, day: datetime.date) -> bool:
    '''
    Given a currently unused prompt, set it as one of the the ranked daily for 'day'
    '''
    query = f"UPDATE sprint_prompts SET active_begin=%s, active_end=%s, rated=1 WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cur:
        res = cur.execute(query, (day, day + datetime.timedelta(days=1, seconds=-1), prompt_id))
        db.commit()
        return res == 1

def set_prompt_time(prompt_id: int, prompt_type: PromptType, active_begin: datetime.date, active_end: datetime.date) -> bool:
    '''
    Given a currently unused prompt, set the active period to [start_day, end_day)
    '''
    query = f"UPDATE {prompt_type}_prompts SET active_begin=%s, active_end=%s WHERE prompt_id=%s"
    db = get_db()
    with db.cursor() as cur:
        res = cur.execute(query, (active_begin, active_end - datetime.timedelta(seconds=1), prompt_id))
        db.commit()
        return res == 1


def get_prompt(prompt_id: int, prompt_type: PromptType) -> Optional[Prompt]:
    ''' 
    Get a specific prompt
    '''
    if (prompt_type == "sprint"):
        query = "SELECT start, end, rated, active_start, active_end FROM sprint_prompts WHERE prompt_id=%s"
    # elif (prompt_type == "marathon")

    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query, (prompt_id,))
        return cur.fetchone()

        


def get_active_prompts(prompt_type: PromptType) -> List[Prompt]:
    '''
    Get all prompts for display on front page (only show start)
    '''
    if (prompt_type == "sprint"):
        query = "SELECT start, NULL as end, rated, active_start, active_end FROM sprint_prompts"
    # elif (prompt_type == "marathon")

    query += " WHERE used = 1 AND active_start <= NOW() AND NOW() < active_end"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()


def get_archive_prompts(prompt_type: PromptType) -> List[Prompt]:
    '''
    Get all prompts for archive, including currently active
    TODO paginate
    '''
    if (prompt_type == "sprint"):
        query = "SELECT start, rated, active_start, active_end FROM sprint_prompts"
    # elif (prompt_type == "marathon")

    query += " WHERE used = 1 AND active_start <= NOW()"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()


def get_managed_prompts(prompt_type: PromptType) -> List[Prompt]:
    '''
    Get all prompts for admins, all active, unused, and upcoming prompts
    '''
    if (prompt_type == "sprint"):
        query = "SELECT start, end, rated, active_start, active_end FROM sprint_prompts"
    # elif (prompt_type == "marathon")

    query += " WHERE used = 0 OR active_end <= NOW()"
    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()