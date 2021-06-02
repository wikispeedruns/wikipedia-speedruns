from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session

from db import get_db
from pymysql.cursors import DictCursor

prompt_api = Blueprint('prompts', __name__, url_prefix='/api/prompts')


@prompt_api.post('/')
@check_admin
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


@prompt_api.get('/')
def get_all_prompts():
    # TODO this should probably be paginated, and return just ids
    query = "SELECT * FROM prompts"

    if (request.args.get("public") == "true"):
        query += " WHERE public=TRUE"
    else:
        # user needs to be logged in to see ranked prompts
        if ("user_id" not in session):
            return "User account required to see this", 401

        if (request.args.get("public") == "false"):
            query += " WHERE public=FALSE"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)


@prompt_api.get('/<id>')
def get_prompt(id):
    # TODO this could probably return details as well
    query = "SELECT * FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        results = cursor.fetchone()
        return jsonify(results)


@prompt_api.patch('/<id>/changepublic')
def set_prompt_publicity(id):
    '''
    Change wheter a prompt is public

    Example json
    {
        "public": true
    }
    '''
    query = "UPDATE prompts SET `public`=%s WHERE `prompt_id`=%s"

    if ("public" not in request.json):
        return "invalid request", 400

    public = request.json["public"]

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        res = cursor.execute(query, (public, id))

        if (res == 0): return "prompt not found", 404
        return "Changed prompt to {}".format("public" if public else "ranked"), 200


@prompt_api.get('/<id>/runs')
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