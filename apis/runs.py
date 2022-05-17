from click import prompt
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


@run_api.patch('/sprints/<int:prompt_id>/runs/<int:run_id>', defaults={'lobby_id' : None})
@run_api.patch("/lobbys/<int:lobby_id>/prompts/<int:prompt_id>/runs/<int:run_id>")
@check_request_json({'start_time': int, 'end_time': int, 'finished': bool, 'path': list})
def update_run(prompt_id, lobby_id, run_id):
    '''
    Updates an existing run given a run, start time, end time, a finished flag, and a path.

    Returns the run ID of the run updated.
    '''
    if lobby_id is None:
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
