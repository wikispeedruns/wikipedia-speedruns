from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session
import json

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





@prompt_api.post('/marathon/')
@check_admin
def create_marathon_prompt():
    # TODO is this the best way to do this?
    query = "INSERT INTO marathonprompts (start, checkpoint1, checkpoint2, checkpoint3, checkpoint4, checkpoint5, seed) VALUES (%s, %s, %s, %s, %s, %s, %s);"

    start = request.json['start']
    cp1 = request.json['cp1']
    cp2 = request.json['cp2']
    cp3 = request.json['cp3']
    cp4 = request.json['cp4']
    cp5 = request.json['cp5']
    seed = request.json['seed']

    print(start, cp1, cp2, cp3, cp4, cp5, seed)

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, cp1, cp2, cp3, cp4, cp5, seed))
        db.commit()
        return "Prompt added!"

    return "Error adding prompt"





@prompt_api.get('')
def get_all_prompts():
    # TODO this should probably be paginated
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
    
    
    
@prompt_api.get('/marathon')
def get_all_marathon_prompts():
    # TODO this should probably be paginated
    query = "SELECT * FROM marathonprompts"

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


@prompt_api.get('/marathon/<id>')
def get_marathon_prompt(id):
    # TODO this could probably return details as well
    query = "SELECT * FROM marathonprompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        results = cursor.fetchone()

        if (not results["public"] and "user_id" not in session):
            return "User account required to see this", 401

        return jsonify(results)


@prompt_api.get('/<id>')
def get_prompt(id):
    # TODO this could probably return details as well
    query = "SELECT * FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        results = cursor.fetchone()

        if (not results["public"] and "user_id" not in session):
            return "User account required to see this", 401


        return jsonify(results)


@prompt_api.patch('/<id>/changepublic')
@check_admin
def set_prompt_publicity(id):
    '''
    Change whether a prompt is public

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

        db.commit()
        return "Changed prompt to {}".format("public" if public else "ranked"), 200
    
    
    
    
    
@prompt_api.patch('/<id>/marathon/changepublic')
@check_admin
def set_marathon_prompt_publicity(id):
    '''
    Change whether a prompt is public

    Example json
    {
        "public": true
    }
    '''
    query = "UPDATE marathonprompts SET `public`=%s WHERE `prompt_id`=%s"

    if ("public" not in request.json):
        return "invalid request", 400

    public = request.json["public"]

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        res = cursor.execute(query, (public, id))

        if (res == 0): return "prompt not found", 404

        db.commit()
        return "Changed prompt to {}".format("public" if public else "ranked"), 200
    
    
    


@prompt_api.get('/<id>/leaderboard/', defaults={'run_id' : None})
@prompt_api.get('/<id>/leaderboard/<run_id>')
def get_prompt_leaderboard(id, run_id):
    # TODO this could probably return details as well
    query = '''
    SELECT run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM runs
    JOIN (
            SELECT users.user_id, username, MIN(start_time) AS first_run 
            FROM runs
            JOIN users ON users.user_id=runs.user_id
            WHERE prompt_id=%s AND end_time IS NOT NULL
            GROUP BY user_id
    ) firsts
    ON firsts.user_id=runs.user_id AND first_run=start_time
    '''

    args = [id]

    specificRunQuery = '''
    SELECT runs.run_id, path, runs.user_id, username, TIMESTAMPDIFF(MICROSECOND, runs.start_time, runs.end_time) AS run_time
    FROM runs
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