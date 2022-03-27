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
    #print(request.json)
    
    start = request.json.get('start')
    end = request.json.get('end')

    if (start is None or end is None): return "Invalid Request", 400

    id = prompts.add_sprint_prompt(start, end)
    return f"Created prompt {id}", 200


@sprint_api.delete('/<id>')
@check_admin
def delete_prompt(id):
    try:
        if prompts.delete_prompt(id, "sprint"):
            return "Prompt deleted!", 200
        else:
            return "Could not delete prompt, may already have run(s)", 400
    except prompts.PromptNotFoundError:
        return "Prompt {id} not found!", 404

@sprint_api.patch('/<id>')
@check_admin
@check_request_json({"startDate": str, "endDate": str, "rated": bool})
def set_prompt_active_time(id):
    '''
    Change whether a prompt is public, daily, or unsued

    Example json inputs
    {
        "startDate": "2020-10-20"      // <---- ISO Date
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
        start_date = datetime.date.fromisoformat(request.json.get("startDate", ""))
        end_date = datetime.date.fromisoformat(request.json.get("endDate", ""))
        rated = request.json.get("rated")
    except (KeyError, ValueError) as e:
        return f"Invalid input", 400


    try:

        if (rated):
            prompts.set_ranked_daily_prompt(id, start_date)
            return f"Set prompt {id} as daily ranked for {start_date}", 200

        else:
            prompts.set_prompt_time(id, "sprint", start_date, end_date)
            return f"Set prompt {id} active from {start_date} to {end_date}", 200

    except prompts.PromptNotFoundError:
        return "Prompt {id} not found!", 404


### Prompt Search Endpoints
@sprint_api.get('/managed')
@check_admin
def get_managed_prompts():
    return jsonify(prompts.get_managed_prompts("sprint"))

@sprint_api.get('/active')
def get_active_prompts():
    return jsonify(prompts.get_active_prompts("sprint", user_id=session.get("user_id")))

@sprint_api.get('/archive')
def get_archive_prompts():
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        sort_desc = request.args.get('sort_desc', "True").lower() == "true"
        sprints, num_prompts = prompts.get_archive_prompts("sprint",
            offset=offset,
            limit=limit,
            sort_desc=sort_desc,
            user_id=session.get("user_id")
        )

        return jsonify({
            "prompts": sprints,
            "numPrompts": num_prompts
        })

    except ValueError:
        return "Invalid limit or offset", 400

### Specific prompt endpoints

@sprint_api.get('/<int:id>')
def get_prompt(id):
    prompt = prompts.get_prompt(id, "sprint", session.get("user_id"))

    if (prompt is None):
        return "Prompt does not exist", 404

    if (session.get("admin")):
        return prompt

    if not prompt["used"]:
        return "Prompt does not exist", 404

    if not prompt["available"]:
        return "Prompt not yet available", 401

    if prompt["rated"] and prompt["active"] and "user_id" not in session:
        return "You must be logged in to play this rated prompt", 401

    return prompt



@sprint_api.get('/<int:id>/leaderboard/', defaults={'run_id' : None})
@sprint_api.get('/<int:id>/leaderboard/<int:run_id>')
def get_prompt_leaderboard(id, run_id):
    # First get the prompt details, and the string
    user_id = session.get("user_id")
    prompt = prompts.get_prompt(id, "sprint", user_id=user_id)

    if not session.get("admin", False) and (prompt["active"] and prompt["rated"] and not prompt.get("played", False)):
        return "Cannot view leaderboard of currently rated prompt until played", 401

    resp = {
        "prompt": prompt
    }

    # Then query the leaderboard (ew)
    query = '''
    SELECT run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time, runs.end_time AS end_time
    FROM sprint_runs AS runs
    JOIN (
            SELECT users.user_id, username, MIN(run_id) AS first_run
            FROM sprint_runs AS runs
            JOIN users ON users.user_id=runs.user_id
            WHERE prompt_id=%s
            GROUP BY user_id
    ) firsts
    ON firsts.user_id=runs.user_id AND first_run=run_id
    WHERE end_time IS NOT NULL
    '''

    args = [id]

    specificRunQuery = '''
    SELECT runs.run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time, runs.end_time AS end_time
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
        cursor.execute(query, tuple(args))
        results = cursor.fetchall()

        for run in results:
            run['path'] = json.loads(run['path'])
            if run_id is None and user_id is not None and run['user_id'] == user_id:
                run_id = run['run_id']

        resp["leaderboard"] = results
        resp["run_id"] = run_id

        return jsonify(resp)
