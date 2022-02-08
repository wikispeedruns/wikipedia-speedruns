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
        "endDate": "2020-10-20"
        "rated": true
    }

    {
        "startDate": "2020-10-20"      // <---- ISO Date
        "endDate": "2020-10-27"
        "rated": false
    }

    '''

    try:
        start_date = datetime.date.fromisoformat(request.json.get("date", ""))
        end_date = request.json.get("endDate")
        rated = request.json.get("rated")
    except (KeyError, ValueError) as e:
        return f"Invalid input", 400

    if (rated):
        prompts.set_ranked_daily_prompt(id, start_date)
    else:
        prompts.set_ranked_daily_prompt(id, end_date)

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
    prompt = get_prompt(id, "sprint")

    if (prompt is None):
        return "Prompt does not exist", 404

    if (session.get("admin")):
        return prompt

    if not prompt["used"]:
        return "Prompt does not exist", 404

    if not prompt["available"]:
        return "Prompt not yet available", 401

    return prompt



@sprint_api.get('/<id>/leaderboard/', defaults={'run_id' : None})
@sprint_api.get('/<id>/leaderboard/<run_id>')
def get_prompt_leaderboard(id, run_id):
    # TODO this could probably return details as well
    # TODO this should restrict viewing to those who have already played, especially for ranked
    query = '''
    SELECT run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM sprint_runs AS runs
    JOIN (
            SELECT users.user_id, username, MIN(start_time) AS first_run 
            FROM sprint_runs AS runs
            JOIN users ON users.user_id=runs.user_id
            WHERE prompt_id=%s AND end_time IS NOT NULL
            GROUP BY user_id
    ) firsts
    ON firsts.user_id=runs.user_id AND first_run=start_time
    '''

    args = [id]

    specificRunQuery = '''
    SELECT runs.run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM sprint_runs AS runs
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