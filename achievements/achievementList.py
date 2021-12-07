from achievement import achievement
import pymysql

achievements = {}

def runContains(run, article):
    pathArr = parseRunForPath(run)
    for a in pathArr:
        if a == article:
            return True
    return False

def parseRunForPath(run):
    return run['path'].split(',')

def checkAllAchievementsAgainstRun(run):
    outputDict = {}
    achievementNames = list(achievements.keys())
    for a in achievementNames:
        if achievements[a].runSpecific:
            outputDict[a] = achievements[a].checkRun(run)
            
    return outputDict


def baby_steps_eval(run):
    return True
baby_steps = achievement("Baby Steps",
                         "Complete a ranked prompt",
                         baby_steps_eval,
                         imgLink = "icons/baby_steps.png",
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
                   imgLink = "icons/meta.png",
                   runSpecific=True,
                   secret=False)
achievements[meta.name] = meta


def you_lost_eval(run):
    pathArr = parseRunForPath(run)
    pathArr.sort()
    for i in range(len(pathArr)):
        if pathArr[i] == pathArr[i+1]:
            return True
    return False
you_lost = achievement("You Lost?",
                       "Arrive at the same page twice in the same run",
                       you_lost_eval,
                       imgLink = "icons/you_lost.png",
                       runSpecific=True,
                       secret=False)
achievements[you_lost.name] = you_lost


if __name__ == '__main__':
    
    db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="wikipedia_speedruns")
    cur = db.cursor(pymysql.cursors.DictCursor)
    
    queryString = "SELECT max(run_id) FROM runs;"
    cur.execute(queryString)
    maxID = int(cur.fetchall()[0]['max(run_id)'])
    
    queryString = "SELECT * FROM runs WHERE run_id=%s;"
    cur.execute(queryString, str(maxID))
    runDict = cur.fetchall()[0]
    
    
    print(checkAllAchievementsAgainstRun(runDict))  
    