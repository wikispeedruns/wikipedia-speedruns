'''
Create some example users/prompts/runs etc. for local dev
'''
import datetime
import pymysql
import json

import bcrypt
import hashlib
import base64

import argparse
import os

DEFAULT_DB_NAME='wikipedia_speedruns'

def populate_sprints(cursor):
    # Create a bunch of daily prompts of the form '[n] (number)' -> '[n + 1] (number)'
    # 20 - 50 are dailys starting from 15 days ago
    # 50 - 60 are unused
    prompts = []

    now = datetime.datetime.now()

    for i in range(40):
        prompt_start = f"{20 + i} (number)"
        prompt_end = f"{20 + i + 1} (number)"
        day = (now - datetime.timedelta(days=(15 - i))).date()
        prompts.append((prompt_start, prompt_end, day, day + datetime.timedelta(days=1)))

    query = '''
        INSERT INTO `sprint_prompts` (`start`, `end`, `rated`, `active_start`, `active_end`)
        VALUES (%s, %s, 1, %s, %s)
    '''
    cursor.executemany(query, prompts[:30])

    # unused prompts
    query = '''
        INSERT INTO `sprint_prompts` (`start`, `end`)
        VALUES (%s, %s)
    '''
    cursor.executemany(query, [(start, end) for (start, end, _, _) in prompts[30:]])
    
    
def populate_marathon_prompts(cursor):
    # Create a bunch of marathon prompts
    prompts = []
    checkpoints = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    for i in range(40):
        checkpoints.append(f"{20 + i} (number)")
        
    for i in range(10):
        reordered = checkpoints[2*i:] + checkpoints[:2*i] 
        start = reordered[0]
        startcps = reordered[1:6]
        cps = reordered[6:]
        seed = i
        prompts.append((start, json.dumps(startcps), seed, json.dumps(cps)))    

    query = "INSERT INTO `marathonprompts` (start, initcheckpoints, seed, checkpoints) VALUES (%s, %s, %s, %s);"
    cursor.executemany(query, prompts)


def populate_users(cursor):
    # Create 40 users with username/password of testuser[i]/testuser[i] for i 1-40
    query = "INSERT INTO `users` (`username`, `hash`, `email`, `join_date`) VALUES (%s, %s, %s, %s)"

    users = []
    date = datetime.datetime.now() - datetime.timedelta(days=40)
    for i in range(40):
        username = f"testuser{i+1}"
        hash = bcrypt.hashpw(base64.b64encode(hashlib.sha256(username.encode()).digest()), bcrypt.gensalt())
        email = username + "@testemail.com"
        date = date + datetime.timedelta(days=1)
        users.append((username, hash, email, date))

    try:
        cursor.executemany(query, users)
    except pymysql.IntegrityError as e:
        print("testuser(s) already exist, continuing...")


def populate_runs(cursor):
    # Create a run for each user on all currently archived prompts
    users_query = "SELECT user_id FROM users"
    prompts_query = """
        SELECT prompt_id, start, end, active_start, active_end FROM sprint_prompts
        WHERE used=1 AND active_start <= NOW()
    """
    runs_query = """
        INSERT INTO sprint_runs (prompt_id, user_id, start_time, end_time, path)
        VALUES (%(prompt_id)s, %(user_id)s, %(start_time)s, %(end_time)s, %(path)s)
    """

    cursor.execute(users_query)
    users = cursor.fetchall()

    cursor.execute(prompts_query)
    prompts = cursor.fetchall()

    runs = []
    for p in prompts:
        if (p['active_start'] is None): continue

        run_time = 50

        for u in users:
            start_time = p["active_start"] + datetime.timedelta(hours=4)
            end_time = p["active_start"] + datetime.timedelta(hours=4, seconds=run_time)
            path = json.dumps([p["start"], p["end"]])

            runs.append({
                "prompt_id": p["prompt_id"],
                "user_id": u["user_id"],
                "start_time": start_time,
                "end_time": end_time,
                "path": path,
            })
            run_time += 20


    cursor.executemany(runs_query, runs)
    
    
def populate_marathon_runs(cursor):
    # Create a run for each user on all marathon prompts
    users_query = "SELECT user_id FROM users"
    prompts_query = """
        SELECT prompt_id, start, initcheckpoints, checkpoints FROM marathonprompts
    """
    runs_query = "INSERT INTO `marathonruns` (`path`, `prompt_id`, `user_id`, `checkpoints`, `total_time`, `finished`) VALUES (%s, %s, %s, %s, %s, %s)"

    cursor.execute(users_query)
    users = cursor.fetchall()

    cursor.execute(prompts_query)
    prompts = cursor.fetchall()

    runs = []
    count = 0
    
    for p in prompts:

        run_time = 10000
        startcp = json.loads(p['initcheckpoints'])
        cp = json.loads(p['checkpoints'])

        for u in users:
            
            path1 = json.dumps([p["start"], startcp[0], startcp[1], cp[0]])
            checkpoints1 = json.dumps([startcp[0], startcp[1], cp[0]])
            
            path2 = json.dumps([p["start"], startcp[0], startcp[1]] + cp[:5])
            checkpoints2 = json.dumps([startcp[0], startcp[1]] + cp[:5])

            runs.append((
                path1,
                p["prompt_id"],
                u["user_id"],
                checkpoints1,
                run_time,
                count%2
            ))
            
            count += 1
            run_time += 200
            runs.append((
                path2,
                p["prompt_id"],
                u["user_id"],
                checkpoints2,
                run_time,
                count%2
            ))
            count += 1

    cursor.executemany(runs_query, runs)



def populate_database(db_name, recreate=False):
    # Load database settings from
    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=db_name
    )


    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        populate_sprints(cursor)
        populate_users(cursor)
        populate_runs(cursor)
        populate_marathon_prompts(cursor)
        populate_marathon_runs(cursor)

        conn.commit()
        conn.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create the db for wikispeedruns.')
    parser.add_argument('--db_name', default=DEFAULT_DB_NAME)

    args = parser.parse_args()
    populate_database(args.db_name)

