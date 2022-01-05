from flask import jsonify, request, Blueprint, session

from db import get_db
from pymysql.cursors import DictCursor

import json

from datetime import datetime


run_api = Blueprint('runs', __name__, url_prefix='/api/runs')


@run_api.post('')
def create_run():
    query = "INSERT INTO `runs` (`start_time`, `end_time`, `path`, `prompt_id`, `user_id`) VALUES (%s, %s, %s, %s, %s)"
    sel_query = "SELECT LAST_INSERT_ID()"

    # datetime wants timestamp in seconds since epoch
    start_time = datetime.fromtimestamp(request.json['start_time']/1000)
    end_time = datetime.fromtimestamp(request.json['end_time']/1000)
    path = json.dumps(request.json['path'])
    prompt_id = request.json['prompt_id']

    if ('user_id' in session):
        user_id = session['user_id']
    else:
        user_id = None

    # TODO validate

    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (start_time, end_time, path, prompt_id, user_id)))
        result = cursor.execute(query, (start_time, end_time, path, prompt_id, user_id))
        
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify(id)

    return "Error submitting prompt"