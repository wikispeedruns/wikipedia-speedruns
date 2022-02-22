from util.decorators import check_admin
from flask import Flask, jsonify, request, Blueprint, session
import json

from db import get_db
from pymysql.cursors import DictCursor


from wikispeedruns.marathon import genPrompts

marathon_api = Blueprint('marathon', __name__, url_prefix='/api/marathon')


@marathon_api.post('/runs/')
def create_run():
    query = "INSERT INTO `marathonruns` (`path`, `prompt_id`, `user_id`, `checkpoints`, `total_time`) VALUES (%s, %s, %s, %s, %s)"
    sel_query = "SELECT LAST_INSERT_ID()"

    # datetime wants timestamp in seconds since epoch
    path = json.dumps(request.json['path'])
    checkpoints = json.dumps(request.json['checkpoints'])
    
    print(checkpoints)
    
    prompt_id = request.json['prompt_id']
    time = str(request.json['time'])

    if ('user_id' in session):
        user_id = session['user_id']
    else:
        user_id = None

    # TODO validate

    db = get_db()
    with db.cursor() as cursor:
        print(cursor.mogrify(query, (path, prompt_id, user_id, checkpoints, time)))
        result = cursor.execute(query, (path, prompt_id, user_id, checkpoints, time))
        
        cursor.execute(sel_query)
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify(id)

    return "Error submitting prompt"


@marathon_api.post('/gen/')
@check_admin
def create_marathon_prompt():
    
    print("Received marathon prompt req")
    print(request.json)
    

    nbucket = int(request.json.get("nbucket"))
    nbatch = int(request.json.get("nbatch"))
    nperbatch = int(request.json.get("nperbatch"))
    
    if nbucket < 1 or nbatch < 1 or nperbatch < 1:
        raise ValueError("Bad input")
    
    
    start = request.json.get("start")
    cp1 = request.json.get("cp1")
    cp2 = request.json.get("cp2")
    cp3 = request.json.get("cp3")
    cp4 = request.json.get("cp4")
    cp5 = request.json.get("cp5")
    seed = request.json.get("seed")
    
    initcheckpoints = [cp1, cp2, cp3, cp4, cp5]
    
    print("Starting prompt generation")
    
    checkpoints = genPrompts(initcheckpoints, batches=nbatch, nPerBatch=nperbatch, buckets=nbucket)

    print("Finished prompt generation")
    
    output = {'start': start,
              'seed': seed,
              'initcheckpoints': initcheckpoints,
              'checkpoints': checkpoints}
    
    return json.dumps(output)

    

@marathon_api.post('/add/')
@check_admin
def add_marathon_prompt():
    print("Received add marathon prompt req")
    #print(request.json)
    
    data = json.loads(request.json.get("data"))
    
    print(data)
    
    start = data['start']
    initcheckpoints = data['initcheckpoints']
    seed = data['seed']
    checkpoints = data['checkpoints']
    
    query = "INSERT INTO `marathonprompts` (start, initcheckpoints, seed, checkpoints) VALUES (%s, %s, %s, %s);"
    db = get_db()
    with db.cursor() as cursor:
        result = cursor.execute(query, (start, json.dumps(initcheckpoints), seed, json.dumps(checkpoints)))
        db.commit()
        return "Prompt added!"


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
            if run['total_time'] is None:
                run['total_time'] = 9999.99

        return jsonify(results)