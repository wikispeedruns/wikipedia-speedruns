from flask import jsonify, request, Blueprint, session

from db import get_db
from pymysql.cursors import DictCursor

import json

from datetime import datetime


run_api = Blueprint('runs', __name__, url_prefix='/api/runs')


@run_api.post('')
def create_run():
    '''
    Creates a new run given a prompt.

    Returns the user ID of the run created.
    '''

    query = "INSERT INTO `runs` (`start_time`,`prompt_id`,`user_id`) VALUES (%s, %s, %s)"
    sel_query = "SELECT LAST_INSERT_ID()"

    start_time = datetime.fromtimestamp(request.json['start_time']/1000)
    prompt_id = request.json['prompt_id']

    if ('user_id' in session):
        user_id = session['user_id']
    else:
        user_id = None

    # TODO validate

    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (start_time, prompt_id, user_id)))
        result = cursor.execute(query, (start_time, prompt_id, user_id))
        
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
    query = 'UPDATE `runs` SET `start_time`=%s, `end_time`=%s, `path`=%s WHERE `run_id`=%s'
    
    start_time = datetime.fromtimestamp(request.json['start_time']/1000)
    end_time = datetime.fromtimestamp(request.json['end_time']/1000)
    path = json.dumps(request.json['path'])

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (start_time, end_time, path, id))
        db.commit()

        return f'Updated run {id}', 200

    return f'Error updating run {id}', 500


@run_api.get('')
def get_all_runs():
    # TODO this should probably be paginated, and return just ids
    query = "SELECT run_id FROM `runs`"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)
    
