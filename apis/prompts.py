import pymysql
from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session

import json
import datetime

from db import get_db
from pymysql.cursors import DictCursor

prompt_api = Blueprint('prompts', __name__, url_prefix='/api/prompts')


### Prompt Management Endpoints
@prompt_api.post('/')
@check_admin
def create_prompt():
    query = "INSERT INTO prompts (start, end) VALUES (%s, %s);"

    start = request.json['start']
    end = request.json['end']

    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, end))
        db.commit()
        return "Prompt added!"


@prompt_api.delete('/<id>')
@check_admin
def delete_prompt(id):
    query = "DELETE FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(query, (id))
            db.commit()
            return "Prompt deleted!", 200
        
        except pymysql.IntegrityError:
            return "Integrity error, prompt may already have run(s)", 400


@prompt_api.patch('/<id>/type')
@check_admin
def set_prompt_type(id):
    '''
    Change whether a prompt is public, daily, or unsued

    Example json inputs
    {
        "type": "public"
    }
    ...
    {
        "type: "unused"
    }
    ...
    {
        "type": "daily"
        "date": "2020-10-20"      // <---- ISO Date
        "rated": true
    }

    '''
    query = "UPDATE prompts SET `type`=%s WHERE `prompt_id`=%s"
    db = get_db()

    prompt_type = request.json.get("type")

    if prompt_type == "public" or prompt_type == "unused":

        with db.cursor(cursor=DictCursor) as cursor:
            res = cursor.execute(query, (prompt_type, id))
            if (res == 0): return "Prompt not found", 404  # TODO this also is true if it's not changed
            db.commit()
            return f"Changed prompt to {prompt_type}", 200

    elif prompt_type == "daily":

        try:
            date = datetime.date.fromisoformat(request.json.get("date", "")) # "" to raise ValueError
            rated = request.json.get("rated", False)
        except (KeyError, ValueError) as e:
            return f"Invalid input", 400

        daily_query = "REPLACE INTO daily_prompts (date, prompt_id, rated) VALUES (%s, %s, %s)"

        with db.cursor(cursor=DictCursor) as cursor:

            # TODO Error check for non existent prompt
            res = cursor.execute(query, (prompt_type, id)) 
            cursor.execute(daily_query, (date, id, rated))
            db.commit()
            return f"Changed prompt to {prompt_type} for {date} (rated: {rated}", 200

    else:
        return "Invalid input", 400


### Prompt Search Endpoints
@prompt_api.get('/all')
@check_admin
def get_all_prompts():
    query = """
    SELECT p.prompt_id, start, end, type, d.date, d.rated
    FROM prompts AS p
    LEFT JOIN daily_prompts as d ON p.prompt_id = d.prompt_id
    """

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

        for p in results:
            if (p["date"]): p["date"] = p["date"].isoformat()

        return jsonify(results)



@prompt_api.get('/public')
def get_public_prompts():
    query = "SELECT prompt_id, start FROM prompts WHERE type='PUBLIC'"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)


@prompt_api.get('/daily')
def get_daily_prompts():
    query = """
    SELECT p.prompt_id, start, d.date, d.rated 
    FROM prompts as p
    JOIN daily_prompts as d ON p.prompt_id = d.prompt_id
    WHERE type='DAILY' 
	    AND d.date <= CURDATE()
        AND d.date > CURDATE() - %s;
    """

    # how many days to look back for daily prompts, defaults to 1
    # TODO add more of these params
    count = request.args.get('count', 1)

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (count, ))
        results = cursor.fetchall()
        return jsonify(results)


### Specific prompt endpoints

@prompt_api.get('/<id>')
def get_prompt(id):
    query = "SELECT prompt_id, start, end, type FROM prompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        prompt = cursor.fetchone()

        # Check permissions for users
        if (not session.get("admin")):
            if (prompt["type"] == "unused"):
                return "You do not have permission to view this prompt", 401

            if (prompt["type"] == "daily"):

                # TODO move this logic into separate logic that maybe returns a dict?
                daily_query = "SELECT date, rated FROM daily_prompts WHERE prompt_id=%s"
                cursor.execute(daily_query, (id,))                
                daily_prompt = cursor.fetchone()

                today = datetime.date.today()
                if (today < daily_prompt["date"]):
                    return "This prompt is not avaiable yet", 401

                if ("user_id" not in session and daily_prompt["rated"] and daily_prompt["date"] == today):
                    return "Login to see this rated prompt", 401
                    
        return jsonify(prompt)



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