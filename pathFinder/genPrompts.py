import pymysql
import time
from dbsearch import getLinks
from dbsearch import getSrc
from dbcreation import log
import random


start_time = time.time()
n = 20
d = 15
thresholdStart = 100

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

def randStart():
    
    queryString = "SELECT max(edgeID) FROM edges;"
    cur.execute(queryString)
    maxID = int(cur.fetchall()[0]['max(edgeID)'])
    
    while True:
        randIndex = random.randint(1, maxID)
        start = getSrc(randIndex, cur)
        if checkStart(start):
            yield start
        #else:
            #log("Not long enough start: " + start)
        
def checkStart(start):
    if len(start) > 7:
        if start[0:7] == "List of":
            return False
    if numLinksOnArticle(start) < thresholdStart:
        return False
    
    return True

def checkEnd(end):
    if len(end) > 7:
        if end[0:7] == "List of":
            return False
    
    if numLinksOnArticle(end) < thresholdStart:
        return False
    
    return True

def numLinksOnArticle(title):
    links = getLinks({title:True}, cur, forward=True)
        
    if title in links:
        links = links[title]
        
        return len(links)
        
    return 0

def traceFromStart(startTitle):

    
    #startTitle = "United States"
    path = []
    
    #dist = int(random.randint(int(-d/2), int(d/2)) + d)
    dist = d
    
    currentTitle = startTitle
    while dist > 0:
        
        path.append(currentTitle)
        
        links = getLinks({currentTitle:True}, cur, forward=True)
        
        if currentTitle in links:
            links = links[currentTitle]
        else:
            break
        
        randIndex = random.randint(0, len(links) - 1)
        
        currentTitle = links[randIndex][0]
        
        dist -= 1
    
    return path + [currentTitle]

def displayGen(arr):
    for path in arr:
        #print(path[0] + " -> " + path[-1] + ":\n " + str(path) + "\n")
        print(path[0] + " -> " + path[-1] + "\n")

def main():
    
    generatedPrompts = []
    
    log("Generating " + str(n) + " prompts")
    
    
    startGenerator = randStart()
    
    while len(generatedPrompts) <= n:
        
        sample = traceFromStart(startGenerator.__next__())
        
        if checkEnd(sample[-1]) and len(sample) == d + 1:
            generatedPrompts.append(sample)
        
    log("Finished generating prompts: \n")
    
    displayGen(generatedPrompts)


if __name__ == "__main__":
    main()