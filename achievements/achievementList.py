from pymysql.cursors import DictCursor
from flask import Blueprint, jsonify

from db import get_db

import json

from .achievementObj.achievementObj import achievement
#import pymysql

achievement_api = Blueprint("achievements", __name__, url_prefix="/api/achievements")

def runContains(run, alist):
    pathArr = parseRunForPath(run)
    for article in alist:
        if not article in pathArr:
            return False
    return True

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

def countArticleInRun(run, article):
    count = 0
    path = parseRunForPath(run)
    for item in path:
        if item == article:
            count += 1
    return count

def countArticleInAllRuns(runs, article):
    count = 0
    for run in runs:
        count += countArticleInRun(run, article)
    return count


def get_all_achievements():
    achievements = {}
    
    def baby_steps_eval(run):
        return True
    baby_steps = achievement("Baby Steps",
                            "Complete a ranked prompt",
                            runEval=baby_steps_eval,
                            imgLink = "/static/assets/achievementIcons/baby_steps.png",
                            runSpecific=True,
                            secret=False)
    achievements[baby_steps.name]=baby_steps


    def meta_eval(run):
        return runContains(run, ["Wikipedia"])
    meta = achievement("Meta",
                    "Arrive at the page: 'Wikipedia'",
                    runEval=meta_eval,
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
                        runEval=you_lost_eval,
                        imgLink = "/static/assets/achievementIcons/you_lost.png",
                        runSpecific=True,
                        secret=False)
    achievements[you_lost.name] = you_lost
    
    def bathroom_break_eval(run):
        return runContains(run, ["Bathroom"])
    bathroom = achievement("Bathroom Break",
                    "Arrive at the page: 'Bathroom'",
                    runEval=bathroom_break_eval,
                    imgLink = "/static/assets/achievementIcons/bathroom.png",
                    runSpecific=True,
                    secret=False)
    achievements[bathroom.name] = bathroom
    
    def rome_eval(run):
        return runContains(run, ["Rome"])
    rome = achievement("All Roads Lead To Rome",
                    "Arrive at the page: 'Rome'",
                    runEval=rome_eval,
                    imgLink = "/static/assets/achievementIcons/rome.png",
                    runSpecific=True,
                    secret=False)
    achievements[rome.name] = rome
    
    def time_is_money_eval(run):
        return runContains(run, ["Currency"])
    time_is_money = achievement("Time Is Money",
                    "Arrive at the page: 'Currency'",
                    runEval=time_is_money_eval,
                    imgLink = "/static/assets/achievementIcons/time_is_money.png",
                    runSpecific=True,
                    secret=False)
    achievements[time_is_money.name] = time_is_money
    
    def luck_of_the_irish_eval(run):
        return runContains(run, ["Ireland"])
    luck_of_the_irish = achievement("Luck Of The Irish",
                    "Arrive at the page: 'Ireland'",
                    runEval=luck_of_the_irish_eval,
                    imgLink = "/static/assets/achievementIcons/luck_of_the_irish.png",
                    runSpecific=True,
                    secret=False)
    achievements[luck_of_the_irish.name] = luck_of_the_irish
    
    def carthage_eval(run):
        return runContains(run, ["Third Punic War", "Cato the Elder"])
    carthage = achievement("Carthago Delenda Est",
                    "Arrive at these pages in the same game: 'Third Punic War', 'Cato the Elder'",
                    runEval=carthage_eval,
                    imgLink = "/static/assets/achievementIcons/carthage.png",
                    runSpecific=True,
                    secret=False)
    achievements[carthage.name] = carthage
    
    def jet_fuel_eval(run):
        return runContains(run, ["Conspiracy theory"])
    jet_fuel = achievement("Jet Fuel Can't Melt Steel Beams",
                    "Arrive at the page: 'Conspiracy theory'",
                    runEval=jet_fuel_eval,
                    imgLink = "/static/assets/achievementIcons/jet_fuel.png",
                    runSpecific=True,
                    secret=False)
    achievements[jet_fuel.name] = jet_fuel
    
    def not_a_crook_eval(run):
        return runContains(run, ["Richard Nixon"])
    not_a_crook = achievement("I am NOT a Crook!",
                    "Arrive at the page: 'Richard Nixon'",
                    runEval=not_a_crook_eval,
                    imgLink = "/static/assets/achievementIcons/not_a_crook.png",
                    runSpecific=True,
                    secret=False)
    achievements[not_a_crook.name] = not_a_crook
    
    def sparta_eval(run):
        return runContains(run, ["Sparta"])
    sparta = achievement("This is Sparta!",
                    "Arrive at the page: 'Sparta'",
                    runEval=sparta_eval,
                    imgLink = "/static/assets/achievementIcons/sparta.png",
                    runSpecific=True,
                    secret=False)
    achievements[sparta.name] = sparta
    
    def simba_eval(run):
        return runContains(run, ["Simba"])
    simba = achievement("Mufasa Would Be Proud",
                    "Arrive at the page: 'Simba'",
                    runEval=simba_eval,
                    imgLink = "/static/assets/achievementIcons/simba.png",
                    runSpecific=True,
                    secret=False)
    achievements[simba.name] = simba
    
    def how_bizarre_eval(run):
        return runContains(run, ["One-hit wonder"])
    how_bizarre = achievement("How Bizarre",
                    "Arrive at the page: 'One-hit wonder'",
                    runEval=how_bizarre_eval,
                    imgLink = "/static/assets/achievementIcons/how_bizarre.png",
                    runSpecific=True,
                    secret=False)
    achievements[how_bizarre.name] = how_bizarre
    
    
    
    def land_of_the_free_eval(username):
        runs = get_user_runs(username)
        return 49 < countArticleInAllRuns(runs, "United States")
    land_of_the_free = achievement("Land of the Free, Home of the Brave",
                                   "Visit 'United States' 50 or more times",
                                   imgLink = "/static/assets/achievementIcons/land_of_the_free.png",
                                   runSpecific=False,
                                   secret=False,
                                   userEval=land_of_the_free_eval)
    achievements[land_of_the_free.name] = land_of_the_free
    
    
    def should_have_went_to_art_school_eval(username):
        runs = get_user_runs(username)
        return 24 < countArticleInAllRuns(runs, "Adolf Hitler")
    should_have_went_to_art_school = achievement("Should Have Went to Art School",
                                   "Visit 'Adolf Hitler' 25 or more times",
                                   imgLink = "/static/assets/achievementIcons/should_have_went_to_art_school.png",
                                   runSpecific=False,
                                   secret=False,
                                   userEval=should_have_went_to_art_school_eval)
    achievements[should_have_went_to_art_school.name] = should_have_went_to_art_school
    
    
    
    
    return achievements

def get_user_runs(username):
    query = "SELECT * FROM runs INNER JOIN users ON runs.user_id = users.user_id WHERE username=%s;"

    with get_db().cursor(cursor=DictCursor) as cursor:
        
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        
        for run in results:
            run['path'] = json.loads(run['path'])

        print(results)

        return results


@achievement_api.get("/user/<username>")
def get_user_achievements(username):
    
    results = get_user_runs(username)

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