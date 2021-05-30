from flask import Flask, jsonify, request, Blueprint

from db import get_db
from pymysql.cursors import DictCursor

prompt_api = Blueprint('prompts', __name__, url_prefix='/api/prompts')


@prompt_api.route('/create', methods=['POST'])
def create_prompt():
    # TODO is this the best way to do this?
    query = "INSERT INTO prompts (start, end) VALUES (%s, %s);"

    start = request.json['start']
    end = request.json['end']

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, end))
        db.commit()
        return "Prompt added!"

    return "Error adding prompt"


@prompt_api.route('/get', methods=['GET'])
def get_all_prompts():
    # TODO this should probably be paginated, and return just ids
    query = "SELECT * FROM prompts"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)


@prompt_api.route('/get/<id>', methods=['GET'])
def get_prompt(id):
    # TODO this could probably return details as well
    query = "SELECT * FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        results = cursor.fetchone()
        return jsonify(results)


@prompt_api.route('/get/<id>/runs', methods=['GET'])
def get_prompt_runs(id):
    # TODO this could probably return details as well
    query = ("""
    SELECT runs.run_id, runs.path, users.user_id, users.username,
            TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM runs 
    INNER JOIN users ON runs.user_id=users.user_id 
    WHERE prompt_id=%s
    ORDER BY run_time 
    """)

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        results = cursor.fetchall()
        return jsonify(results)