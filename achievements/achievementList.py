from pymysql.cursors import DictCursor
from flask import Blueprint, jsonify

from db import get_db

import json

from .achievementObj.achievementObj import achievement
#import pymysql

achievement_api = Blueprint("achievements", __name__, url_prefix="/api/achievements")



def runContains(run, article):
    pathArr = parseRunForPath(run)
    for a in pathArr:
        if a == article:
            return True
    return False

def parseRunForPath(run):
    #print(run)
    #print(run['path'])
    return run['path']

def checkAllAchievementsAgainstRun(run):
    achievements = get_all_achievements()
    outputDict = {}
    achievementNames = list(achievements.keys())
    for a in achievementNames:
        if achievements[a].runSpecific:
            outputDict[a] = achievements[a].checkRun(run)
        else:
            outputDict[a] = False
            
    return outputDict


def get_all_achievements():
    achievements = {}
    
    def baby_steps_eval(run):
        return True
    baby_steps = achievement("Baby Steps",
                            "Complete a ranked prompt",
                            baby_steps_eval,
                            imgLink = "/static/assets/achievementIcons/baby_steps.png",
                            runSpecific=True,
                            secret=False)
    achievements[baby_steps.name]=baby_steps


    def meta_eval(run):
        if runContains(run, "Wikipedia"):
            return True
        return False
    meta = achievement("Meta",
                    "Arrive at the page: 'Wikipedia'",
                    meta_eval,
                    imgLink = "/static/assets/achievementIcons/meta.png",
                    runSpecific=True,
                    secret=False)
    achievements[meta.name] = meta


    def you_lost_eval(run):
        pathArr = parseRunForPath(run)
        pathArr.sort()
        for i in range(len(pathArr)-1):
            if pathArr[i] == pathArr[i+1]:
                return True
        return False
    you_lost = achievement("You Lost?",
                        "Arrive at the same page twice in the same run",
                        you_lost_eval,
                        imgLink = "/static/assets/achievementIcons/you_lost.png",
                        runSpecific=True,
                        secret=False)
    achievements[you_lost.name] = you_lost
    
    
    def test_eval(run):
        return False
    test = achievement("Test",
                        "Test",
                        test_eval,
                        imgLink = "/static/assets/achievementIcons/you_lost.png",
                        runSpecific=True,
                        secret=False)
    achievements[test.name] = test
    
    
    return achievements


@achievement_api.get("/user/<username>")
def get_user_achievements(username):
    
    query = "SELECT * FROM runs INNER JOIN users ON runs.user_id = users.user_id WHERE username=%s;"

    with get_db().cursor(cursor=DictCursor) as cursor:
        
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        
        for run in results:
            run['path'] = json.loads(run['path'])

        #print(results)

    if len(results) == 0:
        return jsonify({})
    
    output = checkAllAchievementsAgainstRun(results[0])
    
    for run in results[1:]:
        runAchievementStatus = checkAllAchievementsAgainstRun(run)
        for a in runAchievementStatus.keys():
            if output[a] == None:
                output[a] = runAchievementStatus[a]
            elif output[a] == False and runAchievementStatus[a] == True:
                output[a] = runAchievementStatus[a]

    #print(output)

    return jsonify(output)


@achievement_api.get("/get_achievements")
def get_achievements():    

    ach = get_all_achievements()
    
    output = {'achievements':[]}
    
    for item in ach.keys():
        a = {}
        a['name'] = ach[item].name
        a['description'] = ach[item].description
        a['imgURL'] = ach[item].imgLink
        a['secret'] = ach[item].secret
        output['achievements'].append(a)
    
    #print(output)
    return jsonify(output)


"""
if __name__ == '__main__':
    
    db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="wikipedia_speedruns")
    cur = db.cursor(pymysql.cursors.DictCursor)
    
    queryString = "SELECT max(run_id) FROM runs;"
    cur.execute(queryString)
    maxID = int(cur.fetchall()[0]['max(run_id)'])
        
    queryString = 
    cur.execute(queryString, str(maxID))
    runDict = cur.fetchall()[0]
    
    
    print(checkAllAchievementsAgainstRun(runDict))  
"""