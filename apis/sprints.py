import pymysql
from flask import Flask, jsonify, request, Blueprint, session

import json
import datetime

from db import get_db
from pymysql.cursors import DictCursor

from util.decorators import check_admin, check_request_json
from wikispeedruns import prompts

sprint_api = Blueprint('sprints', __name__, url_prefix='/api/sprints')


### Prompt Management Endpoints
@sprint_api.post('/')
@check_admin
@check_request_json({"start": str, "end": str})
def create_prompt():
    print(request.json)
    start = request.json.get('start')
    end = request.json.get('end')

    if (start is None or end is None): return "Invalid Request", 400

    id = prompts.add_sprint_prompt(start, end)
    return f"Created prompt {id}", 200


@sprint_api.delete('/<id>')
@check_admin
def delete_prompt(id):
    if prompts.delete_prompt(id):
        return "Prompt deleted!", 200
    else:
        return "Could not delete prompt,  may already have run(s)", 400


@sprint_api.patch('/<id>')
@check_admin
def set_prompt_active_time(id):
    '''
    Change whether a prompt is public, daily, or unsued

    Example json inputs
    {

        "date": "2020-10-20"      // <---- ISO Date
        "rated": true
    }

    '''
    query = "UPDATE prompts SET `type`=%s WHERE `prompt_id`=%s"
    db = get_db()

    prompt_type = request.json.get("type")

    if prompt_type == "public" or prompt_type == "unused":

        with db.cursor(cursor=DictCursor) as cursor:
            res = cursor.execute(query, (prompt_type, id))
            if (res == 0): return "Prompt not found", 404  # TODO this also is true if it's not changed
            db.commit()
            return f"Changed prompt to {prompt_type}", 200

    elif prompt_type == "daily":

        try:
            date = datetime.date.fromisoformat(request.json.get("date", "")) # "" to raise ValueError
            rated = request.json.get("rated", False)
        except (KeyError, ValueError) as e:
            return f"Invalid input", 400

        daily_query = "REPLACE INTO daily_prompts (date, prompt_id, rated) VALUES (%s, %s, %s)"

        with db.cursor(cursor=DictCursor) as cursor:

            # TODO Error check for non existent prompt
            res = cursor.execute(query, (prompt_type, id)) 
            cursor.execute(daily_query, (date, id, rated))
            db.commit()
            return f"Changed prompt to {prompt_type} for {date} (rated: {rated}", 200

    else:
        return "Invalid input", 400


### Prompt Search Endpoints
@sprint_api.get('/managed')
@check_admin
def get_managed_prompts():
    return jsonify(prompts.get_managed_prompts("sprint"))

@sprint_api.get('/active')
def get_active_prompts():
    return jsonify(prompts.get_archive_prompts("sprint"))

@sprint_api.get('/archive')
def get_active_prompts():
    return jsonify(prompts.get_active_prompts("sprint"))


### Specific prompt endpoints

@sprint_api.get('/<id>')
def get_prompt(id):
    query = "SELECT prompt_id, start, end, type FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        prompt = cursor.fetchone()

        # Check permissions for users
        if (not session.get("admin")):
            if (prompt["type"] == "unused"):
                return "You do not have permission to view this prompt", 401

            if (prompt["type"] == "daily"):

                # TODO move this logic into separate logic that maybe returns a dict?
                daily_query = "SELECT date, rated FROM daily_prompts WHERE prompt_id=%s"
                cursor.execute(daily_query, (id,))                
                daily_prompt = cursor.fetchone()

                today = datetime.date.today()
                if (today < daily_prompt["date"]):
                    return "This prompt is not avaiable yet", 401

                if ("user_id" not in session and daily_prompt["rated"] and daily_prompt["date"] == today):
                    return "Login to see this rated prompt", 401
                    
        return jsonify(prompt)



@sprint_api.get('/<id>/leaderboard/', defaults={'run_id' : None})
@sprint_api.get('/<id>/leaderboard/<run_id>')
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