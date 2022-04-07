from flask import jsonify, request, Blueprint, session
from util.decorators import check_user, check_request_json

from db import get_db
from pymysql.cursors import DictCursor

import json

from datetime import datetime
from wikispeedruns import prompts


run_api = Blueprint('runs', __name__, url_prefix='/api/runs')


@run_api.post('')
def create_run():
    '''
    Creates a new run given a prompt.

    Returns the ID of the run created.
    '''

    query = "INSERT INTO `sprint_runs` (`prompt_id`,`user_id`) VALUES (%s, %s)"
    sel_query = "SELECT LAST_INSERT_ID()"

    prompt_id = request.json['prompt_id']

    if ('user_id' in session):
        user_id = session['user_id']
    else:
        user_id = None

    # TODO validate

    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (prompt_id, user_id)))
        cursor.execute(query, (prompt_id, user_id))
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify(id), 200

    return "Error creating run", 500


@run_api.patch('/<id>')
def finish_run(id):
    '''
    Updates an existing run given a run, start time, end time, and a path.

    Returns the user ID of the run updated.
    '''
    query = 'UPDATE `sprint_runs` SET `start_time`=%s, `end_time`=%s, `path`=%s WHERE `run_id`=%s'

    start_time = datetime.fromtimestamp(request.json['start_time']/1000)
    end_time = datetime.fromtimestamp(request.json['end_time']/1000)
    path = json.dumps(request.json['path'])

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (start_time, end_time, path, id))
        db.commit()

        return f'Updated run {id}', 200

    return f'Error updating run {id}', 500


@run_api.patch('/update_anonymous')
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

    return f'Error updating run {run_id} to user {user_id}', 500


@run_api.get('')
def get_all_runs():
    # TODO this should probably be paginated, and return just ids
    query = "SELECT run_id FROM `sprint_runs`"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)

@run_api.get('/<id>')
def get_run(id):
    '''
    Returns the run details for a specific run_id if the user has done the corresponding prompt.
    '''

    query = '''
    SELECT run_id, start_time, end_time, path, prompt_id, user_id
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

        if result["path"] is None:
            return f'Run {id} has not been completed', 401

        result['path'] = json.loads(result['path'])
        return jsonify(result)

    return f'Error fetching run {id}', 500