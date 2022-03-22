
from typing import List, Literal, Tuple, TypedDict, Optional

from db import get_db

import pymysql
from pymysql.cursors import DictCursor

import datetime

# TODO account for marathon prompts here


PromptType = Literal["marathon", "sprint"]

class PromptNotFoundError(Exception):
    pass


class Prompt(TypedDict):
    prompt_id: int
    start: str
    active_start: datetime.datetime
    active_end: datetime.datetime

    used: bool
    available: bool
    active: bool
    played: bool # TODO

class SprintPrompt(Prompt):
    end: Optional[str]
    rated: bool


class MarathonPrompt(Prompt):
    start: str

    # TODO


def compute_visibility(prompt: Prompt) -> Prompt:
    now = datetime.datetime.now()
    prompt["used"] = not (prompt["active_start"] is None or prompt["active_end"] is None)

    if (not prompt["used"]): return prompt

    prompt["available"] = now >= prompt["active_start"]
    prompt["active"] = now >= prompt["active_start"] and now <= prompt["active_end"]
    return prompt

def add_sprint_prompt(start: str, end: str) -> Optional[int]:
    '''
    Add a prompt
    '''
    query = "INSERT INTO sprint_prompts (start, end) VALUES (%s, %s);"
    sel_query = "SELECT LAST_INSERT_ID()"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (start, end))
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()
        return id


def delete_prompt(prompt_id: int, prompt_type: PromptType) -> bool:
    '''
    Delete a prompt, returning whether it could be deleted. Raises exception on not found
    '''

    query = f"DELETE FROM {prompt_type}_prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        try:
            res = cursor.execute(query, (prompt_id))
            if (res == 0): raise PromptNotFoundError()

            db.commit()
            return res == 1

        except pymysql.IntegrityError:
            return False



def set_ranked_daily_prompt(prompt_id: int, day: datetime.date) -> bool:
    '''
    Given a currently unused prompt, set it as one of the the ranked daily for 'day'
    '''
    query = f"UPDATE sprint_prompts SET active_start=%s, active_end=%s, rated=1 WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cur:
        res = cur.execute(query, (day, day + datetime.timedelta(days=1), prompt_id))
        db.commit()
        return res == 1

def set_prompt_time(prompt_id: int, prompt_type: PromptType, active_start: datetime.date, active_end: datetime.date) -> bool:
    '''
    Given a currently unused prompt, set the active period to [start_day, end_day)
    '''
    query = f"UPDATE {prompt_type}_prompts SET active_start=%s, active_end=%s, rated=0 WHERE prompt_id=%s"
    db = get_db()
    with db.cursor() as cur:
        res = cur.execute(query, (active_start, active_end, prompt_id))
        db.commit()

        if (res == 0): raise PromptNotFoundError()
        return res == 1


def get_prompt(prompt_id: int, prompt_type: PromptType, user_id: Optional[int]=None) -> Optional[Prompt]:
    '''
    Get a specific prompt
    '''
    if (prompt_type == "sprint"):
        query = "SELECT prompt_id, start, end, rated, active_start, active_end FROM sprint_prompts WHERE prompt_id=%s"
    # elif (prompt_type == "marathon")

    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query, (prompt_id,))
        prompt = cur.fetchone()

        if (prompt is None):
            return None

        if (user_id is not None):
            cur.execute(f"SELECT COUNT(*) as count FROM {prompt_type}_runs WHERE prompt_id=%s AND user_id=%s", (prompt_id, user_id))
            prompt["played"] = cur.fetchone()["count"] > 0

        prompt = compute_visibility(prompt)
        return prompt

def _construct_prompt_user_query(prompt_type: PromptType, user_id: Optional[int]):

    # 1. Determine which fields are needed
    # if prompt_type == marathon probably change these fields
    fields = ['p.prompt_id', 'start', 'end', 'rated', 'active_start', 'active_end']
    args = {}

    if user_id:
        fields.append('played')

    query = f"SELECT {','.join(fields)} FROM {prompt_type}_prompts AS p"


    # 2. Add neccesary join/args for user info (TODO could in the future get best run?)
    if user_id:
        # TODO returns null on no plays?
        query += '''
        LEFT JOIN  (
            SELECT prompt_id, COUNT(*) AS played
            FROM sprint_runs AS runs
            WHERE user_id=%(user_id)s
            GROUP BY prompt_id
        ) user_runs
        ON user_runs.prompt_id = p.prompt_id
        '''
        args["user_id"] = user_id


    return query, args



def get_active_prompts(prompt_type: PromptType, user_id: Optional[int]=None,) -> List[Prompt]:
    '''
    Get all prompts for display on front page (only show start)
    TODO user id?
    '''

    query, args = _construct_prompt_user_query(prompt_type, user_id)
    query += " WHERE used = 1 AND active_start <= NOW() AND NOW() < active_end"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query, args)

        prompts = cur.fetchall()

        # Remove end for all active prompts
        for p in prompts:
            p['end'] = None

    return prompts

def get_archive_prompts(prompt_type: PromptType, user_id: Optional[int]=None, offset: int=0, limit: int=20, sort_desc: bool=True) -> Tuple[List[Prompt], int]:
    '''
    Get all prompts for archive, including currently active
    '''
    if sort_desc:
        sort = 'DESC'
    else:
        sort = 'ASC'
    if (prompt_type == "sprint"):
        query = "SELECT prompt_id, start, end, rated, active_start, active_end FROM sprint_prompts"
    # elif (prompt_type == "marathon")

    query, args = _construct_prompt_user_query(prompt_type, user_id)
    query += f" WHERE used = 1 AND active_start <= NOW() ORDER BY active_start {sort}, prompt_id {sort} LIMIT %(offset)s, %(limit)s"

    args["offset"] = offset
    args["limit"] = limit

    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query, args)

        prompts = cur.fetchall()

        # remove end prompt from currently active prompts
        for p in prompts:
            compute_visibility(p)
            if (p['active']): p['end'] = None

        # get the total number of prompts
        cur.execute("SELECT COUNT(*) AS n FROM sprint_prompts WHERE used = 1 AND active_start <= NOW()")
        n = cur.fetchone()['n']

        return prompts, n


def get_managed_prompts(prompt_type: PromptType) -> List[Prompt]:
    '''
    Get all prompts for admins, all active, unused, and upcoming prompts
    '''
    if (prompt_type == "sprint"):
        query = "SELECT prompt_id, start, end, rated, active_start, active_end FROM sprint_prompts"
    # elif (prompt_type == "marathon")

    # Minus 7 to see more recently active prompts
    query += " WHERE used = 0 OR active_end >= DATE_ADD(NOW(), INTERVAL -7 DAY)"
    db = get_db()
    with db.cursor(cursor=DictCursor) as cur:
        cur.execute(query)
        return [compute_visibility(p) for p in cur.fetchall()]