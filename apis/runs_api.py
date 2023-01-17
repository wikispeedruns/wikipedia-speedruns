from flask import jsonify, request, Blueprint, session
from util.decorators import check_user, check_request_json

from db import get_db
from pymysql.cursors import DictCursor

import json

from datetime import datetime
from wikispeedruns import prompts, lobbys, runs

# Does not have its own prefix, instead part of the lobbys and sprints apis
run_api = Blueprint('runs', __name__, url_prefix='/api')


@run_api.post('/sprints/<int:prompt_id>/runs')
def create_sprint_run(prompt_id):
    run_id = runs.create_sprint_run(prompt_id, session.get("user_id"))
    return jsonify({"run_id": run_id})

@run_api.post("/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/runs")
def create_lobby_run(prompt_id, lobby_id):
    if not lobbys.check_membership(lobby_id, session):
        return "You do not have access to this lobby", 401

    run_id = runs.create_lobby_run(prompt_id, lobby_id,
        user_id=session.get("user_id"),
        name=session.get("lobbys", {}).get(str(lobby_id))
    )
    return jsonify({"run_id": run_id})

@run_api.post("/quick_runs/runs")
def create_quick_run():
    try:
        prompt_start = request.args.get('prompt_start')
        prompt_end = request.args.get('prompt_end')
        lang = request.args.get('lang', None)
        if prompt_start is None or prompt_end is None or lang is None:
            return "Invalid request", 400
        run_id = runs.create_quick_run(prompt_start, prompt_end, lang, session.get("user_id"))
        return jsonify({"run_id": run_id})
    except ValueError:
        return "Page Not Found", 404

@run_api.patch('/sprints/<int:prompt_id>/runs/<int:run_id>', defaults={'lobby_id' : None})
@run_api.patch("/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/runs/<int:run_id>")
@run_api.patch("/quick_runs/runs/<int:run_id>", defaults={'lobby_id' : None, 'prompt_id': None})
@check_request_json({'start_time': int, 'end_time': int, 'finished': bool, 'path': list})
def update_run(prompt_id, lobby_id, run_id):
    '''
    Updates an existing run given a run, start time, end time, a finished flag, and a path.

    Returns the run ID of the run updated.
    '''
    if prompt_id is None:
        ret_run_id = runs.update_quick_run(
            run_id     = run_id,
            start_time = datetime.fromtimestamp(request.json['start_time']/1000),
            end_time   = datetime.fromtimestamp(request.json['end_time']/1000),
            finished   = request.json['finished'],
            path       = request.json['path']
        )
    elif lobby_id is None:
        ret_run_id = runs.update_sprint_run(
            run_id     = run_id,
            start_time = datetime.fromtimestamp(request.json['start_time']/1000),
            end_time   = datetime.fromtimestamp(request.json['end_time']/1000),
            finished   = request.json['finished'],
            path       = request.json['path']
        )

    else:
        ret_run_id = runs.update_lobby_run(
            run_id     = run_id,
            start_time = datetime.fromtimestamp(request.json['start_time']/1000),
            end_time   = datetime.fromtimestamp(request.json['end_time']/1000),
            finished   = request.json['finished'],
            path       = request.json['path']
        )


    return jsonify({"run_id": ret_run_id})


@run_api.patch('/runs/update_anonymous')
@check_user
@check_request_json({"run_id": int})
def update_anonymous_sprint_run():
    '''
    Updates the user_id of a given run_id, only if the associated run_id is an anonymous run
    '''

    query = 'UPDATE `sprint_runs` SET `user_id`=%s WHERE `run_id`=%s AND `user_id` IS NULL'

    user_id = session['user_id']
    run_id = request.json['run_id']

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (user_id, run_id))
        db.commit()

        return f'Updated run {run_id} to user {user_id}', 200



@run_api.patch('/quick_runs/update_anonymous')
@check_user
@check_request_json({"run_id": int})
def update_anonymous_quick_run():
    query = 'UPDATE `quick_runs` SET `user_id`=%s WHERE `run_id`=%s AND `user_id` IS NULL'

    user_id = session['user_id']
    run_id = request.json['run_id']

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (user_id, run_id))
        db.commit()

        return f'Updated quick run {run_id} to user {user_id}', 200


@run_api.get('/runs')
def get_all_runs():
    # TODO this should probably be paginated, and return just ids
    query = "SELECT run_id FROM `sprint_runs`"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)


@run_api.get('/runs/<id>')
def get_run(id):
    '''
    Returns the run details for a specific run_id if the user has done the corresponding prompt.
    '''

    query = '''
    SELECT run_id, start_time, end_time, play_time, finished, path, prompt_id, user_id
    FROM sprint_runs
    WHERE run_id=%s
    '''

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id))
        result = cursor.fetchone()
        db.commit()

        prompt = prompts.get_prompt(result['prompt_id'], "sprint", user_id=session.get("user_id"))
        if not session.get("admin", False) and (not prompt.get("played", False)):
            return "Cannot view run until prompt has been completed", 401

        if result["finished"] is False:
            return f'Run {id} has not been completed', 401

        result['path'] = json.loads(result['path'])['path']
        return jsonify(result)

    return f'Error fetching run {id}', 500


@run_api.get('/quick_run/runs/<id>')
def get_quick_run(id):

    query = '''
    SELECT run_id, start_time, end_time, play_time, finished, path, prompt_start, prompt_end, user_id, language
    FROM quick_runs
    WHERE run_id=%s
    '''

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id))
        result = cursor.fetchone()
        db.commit()

        if result["finished"] is False:
            return f'Run {id} has not been completed', 401

        result['path'] = json.loads(result['path'])['path']
        return jsonify(result)

    return f'Error fetching run {id}', 500
