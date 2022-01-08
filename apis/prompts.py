from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session

import json
import datetime

from db import get_db
from pymysql.cursors import DictCursor

prompt_api = Blueprint('prompts', __name__, url_prefix='/api/prompts')


### Prompt Management Endpoints
@prompt_api.post('/')
@check_admin
def create_prompt():
    query = "INSERT INTO prompts (start, end) VALUES (%s, %s);"

    start = request.json['start']
    end = request.json['end']

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, end))
        db.commit()
        return "Prompt added!"


@prompt_api.delete('/<id>')
@check_admin
def delete_prompt(id):
    query = "DELETE FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (id))
        db.commit()
        return "Prompt deleted!"


@prompt_api.patch('/<id>/type')
@check_admin
def set_prompt_type(id):
    '''
    Change whether a prompt is public, daily, or unsued

    Example json inputs
    {
        "type": "public"
    }
    ...
    {
        "type: "unused"
    }
    ...
    {
        "type": "daily"
        "date": "2020-10-20"      // <---- ISO Date
        "ranked": true
    }

    '''
    query = "UPDATE prompts SET `type`=%s WHERE `prompt_id`=%s"
    db = get_db()

    prompt_type = request.json.get("type")

    if prompt_type == "public" or prompt_type == "unused":

        with db.cursor(cursor=DictCursor) as cursor:
            res = cursor.execute(query, (prompt_type, id))
            if (res == 0): return "Prompt not found", 404
            db.commit()
            return f"Changed prompt to {prompt_type}", 200

    elif prompt_type == "daily":

        try:
            date = datetime.date.fromisoformat(request.json.get("date", "")) # "" to raise ValueError
            ranked = request.json.get("ranked", False)
        except (KeyError, ValueError):
            return f"Invalid input", 400

        daily_query = "REPLACE INTO daily_prompts (date, prompt_id, ranked)"

        with db.cursor(cursor=DictCursor) as cursor:
            res = cursor.execute(query, (prompt_type, id))
            if (res == 0): return "Prompt not found", 404
            cursor.execute(daily_query, (date, id, ranked))
            db.commit()
            return f"Changed prompt to {prompt_type} for {date} (ranked: {ranked}", 200

    else:
        return "Invalid input", 400


### Prompt Search Endpoints
@prompt_api.get('/public')
def get_public_prompts():
    query = "SELECT start FROM prompts WHERE type='PUBLIC'"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)


@prompt_api.get('/daily')
def get_daily_prompts():
    query = """
    SELECT prompt_id, start 
    FROM prompts as p
    JOIN prompts_daily as d ON p.prompt_id = d.prompt_id
    WHERE type='DAILY' 
        AND d.date <= CURDATE() 
        AND d.date > CURDATE - %s;
    """

    # how many days to look back for daily prompts, defaults to 7
    # TODO add more of these params
    count = request.args.get('count', 7)

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (count, ))
        results = cursor.fetchall()
        return jsonify(results)


### Specific prompt endpoints

@prompt_api.get('/<id>')
def get_prompt(id):
    # TODO this could probably return details as well
    query = "SELECT * FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        results = cursor.fetchone()

        if (not results["public"] and "user_id" not in session):
            return "User account required to see this", 401

        return jsonify(results)



@prompt_api.get('/<id>/leaderboard/', defaults={'run_id' : None})
@prompt_api.get('/<id>/leaderboard/<run_id>')
def get_prompt_leaderboard(id, run_id):
    # TODO this could probably return details as well
    query = '''
    SELECT run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM runs
    JOIN (
            SELECT users.user_id, username, MIN(start_time) AS first_run 
            FROM runs
            JOIN users ON users.user_id=runs.user_id
            WHERE prompt_id=%s AND end_time IS NOT NULL
            GROUP BY user_id
    ) firsts
    ON firsts.user_id=runs.user_id AND first_run=start_time
    '''

    args = [id]

    specificRunQuery = '''
    SELECT runs.run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM runs
    LEFT JOIN users
    ON runs.user_id=users.user_id
    WHERE runs.run_id=%s
    '''

    ordering = f'\nORDER BY run_time'

    if run_id:
        query = f'({query}) UNION ({specificRunQuery})'
        args.append(run_id)

    query += ordering
    
    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        # print(cursor.mogrify(query, tuple(args)))         # debug
        cursor.execute(query, tuple(args))
        results = cursor.fetchall()

        for run in results:
            run['path'] = json.loads(run['path'])

        return jsonify(results)