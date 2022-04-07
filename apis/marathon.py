from util.decorators import check_admin, check_user, check_request_json
from flask import Flask, jsonify, request, Blueprint, session, abort
import json

from db import get_db
from pymysql.cursors import DictCursor


from wikispeedruns.marathon import genPrompts

marathon_api = Blueprint('marathon', __name__, url_prefix='/api/marathon')


@marathon_api.post('/runs/')
def create_run():
    query = "INSERT INTO `marathonruns` (`path`, `prompt_id`, `user_id`, `checkpoints`, `total_time`, `finished`) VALUES (%s, %s, %s, %s, %s, %s)"
    sel_query = "SELECT LAST_INSERT_ID()"

    # datetime wants timestamp in seconds since epoch
    path = json.dumps(request.json['path'])
    checkpoints = json.dumps(request.json['checkpoints'])
    
    prompt_id = request.json['prompt_id']
    time = str(request.json['time'])
    
    finished = str(request.json['finished'])

    if ('user_id' in session):
        user_id = session['user_id']
    else:
        user_id = None

    # TODO validate

    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (path, prompt_id, user_id, checkpoints, time, finished)))
        result = cursor.execute(query, (path, prompt_id, user_id, checkpoints, time, finished))
        
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify(id)

    return "Error submitting prompt"
    
@marathon_api.patch('/update_anonymous')
@check_user
@check_request_json({"run_id": int})
def update_anonymous_marathon_run():
    '''
    Updates the user_id of a given run_id, only if the associated run_id is an anonymous run
    '''

    query = 'UPDATE `marathonruns` SET `user_id`=%s WHERE `run_id`=%s AND `user_id` IS NULL' 
    
    user_id = session['user_id']
    run_id = request.json['run_id']
    
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, (user_id, run_id))
        db.commit()

        return f'Updated marathon run {run_id} to user {user_id}', 200


@marathon_api.post('/add/')
@check_admin
def add_marathon_prompt():
    print("Received add marathon prompt req")
        
    data = request.json.get("data")
    
    print(data)
    
    start = data['start']
    initcheckpoints = data['startcp']
    seed = data['seed']
    checkpoints = data['cp']
    
    query = "INSERT INTO `marathonprompts` (start, initcheckpoints, seed, checkpoints) VALUES (%s, %s, %s, %s);"
    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, json.dumps(initcheckpoints), seed, json.dumps(checkpoints)))
        db.commit()
        return "Prompt added!"
    
    #return "Prompt added!"


@marathon_api.delete('/delete/<id>')
@check_admin
def delete_prompt(id):
    query = "DELETE FROM marathonprompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(query, (id))
            db.commit()
            return "Prompt deleted!", 200
        
        except pymysql.IntegrityError:
            return "Integrity error, prompt may already have run(s)", 400
    

@marathon_api.get('/all')
def get_all_marathon_prompts():
    query = """
    SELECT * FROM marathonprompts
    """

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results)



    
@marathon_api.get('/prompt/<id>')
def get_marathon_prompt(id):
    
    query = "SELECT * FROM marathonprompts WHERE prompt_id=%s"

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (id,))
        prompt = cursor.fetchone()

        # Check permissions for users
        #if (not session.get("admin")):
        #    if (prompt["type"] == "unused"):
        #        return "You do not have permission to view this prompt", 401
                    
        return jsonify(prompt)


@marathon_api.get('/prompt/<id>/leaderboard/', defaults={'run_id' : None})
@marathon_api.get('/prompt/<id>/leaderboard/<run_id>')
def get_marathon_prompt_leaderboard(id, run_id):
    
    # TODO this could probably return details as well
    query = '''
    SELECT * FROM marathonruns
    LEFT JOIN users
    ON marathonruns.user_id=users.user_id
    WHERE marathonruns.prompt_id=%s
    '''

    args = [id]

    specificRunQuery = '''
    SELECT * FROM marathonruns
    LEFT JOIN users
    ON marathonruns.user_id=users.user_id
    WHERE marathonruns.run_id=%s
    '''

    if run_id:
        query = f'({query}) UNION ({specificRunQuery})'
        args.append(run_id)
    
    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        # print(cursor.mogrify(query, tuple(args)))         # debug
        cursor.execute(query, tuple(args))
        results = cursor.fetchall()

        for run in results:
            run['path'] = json.loads(run['path'])
            run['checkpoints'] = json.loads(run['checkpoints'])

        return jsonify(results)
    
    
@marathon_api.get('/<username>')
def get_marathon_personal_leaderboard(username):
        
    if session.get("username") == username or session.get("admin"):
    
        id_query = '''
        SELECT user_id FROM users WHERE users.username=%s
        '''
    
        query = '''
        SELECT marathonruns.checkpoints AS checkpoints, finished, initcheckpoints, marathonruns.prompt_id AS prompt_id, path, run_id, start, total_time
        FROM marathonruns
        LEFT JOIN marathonprompts ON marathonruns.prompt_id=marathonprompts.prompt_id
        WHERE marathonruns.user_id=%s AND initcheckpoints IS NOT NULL
        '''
        
        db = get_db()
        with db.cursor(cursor=DictCursor) as cursor:
            # print(cursor.mogrify(query, tuple(args)))         # debug
            cursor.execute(id_query, (username, ))
            id_res = cursor.fetchone()
            
            #print(id_res)
            cursor.execute(query, (str(id_res['user_id']),))
            results = cursor.fetchall()
            
            print(results)
            
            for run in results:
                run['path'] = json.loads(run['path'])
                run['checkpoints'] = json.loads(run['checkpoints'])
                run['initcheckpoints'] = json.loads(run['initcheckpoints'])
                
            
            return jsonify(results)
        
    abort(404)