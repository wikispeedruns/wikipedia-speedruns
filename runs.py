from flask import Flask, jsonify, request, Blueprint

from db import get_db
from pymysql.cursors import DictCursor

from datetime import datetime


run_api = Blueprint('attempt', __name__, url_prefix='/api/runs')


@run_api.route('/create', methods=['POST'])
def create_run():
    query = "INSERT INTO `runs` (`start_time`, `end_time`, `path`, `prompt_id`) VALUES (%s, %s, %s, %s)"

    # datetime wants timestamp in seconds since epoch
    start_time = datetime.fromtimestamp(request.json['start_time']/1000)
    end_time = datetime.fromtimestamp(request.json['end_time']/1000)
    path = str(request.json['path']) # TODO Format path
    prompt_id = request.json['prompt_id']


    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (start_time, end_time, path, prompt_id)))
        result = cursor.execute(query, (start_time, end_time, path, prompt_id))
        db.commit()

        return "Run Submitted!"

    return "Error submitting prompt"


@run_api.route('/get', methods=['GET'])
def get_all_runs():
    # TODO this should probably be paginated, and return just ids
    query = "SELECT * FROM `runs`"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)


