import pymysql
import time
from dbsearch import getLinks
from dbsearch import getSrc

import random

import bidirectionalSearch as searcher

debugMode = False

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

def randStart(thresholdStart):
    
    queryString = "SELECT max(edgeID) FROM edgeidarticleid;"
    cur.execute(queryString)
    maxID = int(cur.fetchall()[0]['max(edgeID)'])
    
    while True:
        randIndex = random.randint(1, maxID)
        start = getSrc(randIndex, cur)
        if checkStart(start, thresholdStart):
            yield start
        
def checkStart(start, thresholdStart):
    
    title = searcher.convertToArticleName(start)
    
    if len(title) > 7:
        if title[0:7] == "List of":
            return False
    
    x = countWords(title)
    
    if randomFilter(True, 0.0047 *x*x*x - 0.0777*x*x + 0.2244*x + 1.226):
        #print("Random filtered:",start)
        return False
    
    if randomFilter(checkSports(title), 0.1):
        #print("Sports filtered:",start)
        return False
    
    if numLinksOnArticle(start) < thresholdStart:
        return False
    
    return True

def countWords(string):
    counter = 1
    for i in string:
        if i == ' ' or i == '-':
            counter += 1
    return counter

def checkEnd(end, thresholdEnd):
    
    title = searcher.convertToArticleName(end)
    
    if len(title) > 7:
        if title[0:7] == "List of":
            return False
    
    x = countWords(title)
    
    if randomFilter(True, 0.0047 *x*x*x - 0.0777*x*x + 0.2244*x + 1.226):
        #print("Random filtered:",end)
        return False
    
    if randomFilter(checkSports(title), 0.05):
        #print("Sports filtered:",end)
        return False
    
    if numLinksOnArticle(end) < thresholdEnd:
        return False
    
    return True

def randomFilter(bln, chance):
    if bln:
        if random.random() > chance:
            return True
    return False

def checkSports(title):
        
    sportsKeywords = ["League", "season", "football", "rugby", "Championship", "baseball", "basketball", "Season", "Athletics", "Series", "Olympics", "Tennis", "Grand Prix"]
    
    try:
        year = int(title[0:4])
        if year > 1900:
            for word in sportsKeywords:
                if word in title:
                    return True
    except ValueError:
        return False

    return False

def numLinksOnArticle(title):
    links = getLinks({title:True}, cur, forward=True)
        
    if title in links:
        links = links[title]
        
        return len(links)
        
    return 0

def traceFromStart(startTitle, dist):

    path = []
    
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

def generatePrompts(thresholdStart=100, thresholdEnd=100, n=20, dist=15):
    
    generatedPromptPaths = []    
    
    print("Generating " + str(n) + " prompts")
    
    
    startGenerator = randStart(thresholdStart)
    endGenerator = randStart(thresholdEnd)
    
    while len(generatedPromptPaths) <= n:
        
        sample = traceFromStart(startGenerator.__next__(), dist)
        
        if checkEnd(sample[-1], thresholdEnd) and len(sample) == d + 1:
            generatedPromptPaths.append(sample)
            print(sample)
        
        #generatedPromptPaths.append([startGenerator.__next__(), endGenerator.__next__()])
        
    print("Finished generating prompts: \n")
    
    return generatedPromptPaths


if __name__ == "__main__":
    
    n = 100
    d = 25
    thresholdStart = 200
    debugMode = False

    paths = generatePrompts(thresholdStart=thresholdStart, thresholdEnd=thresholdStart, n=n, dist=d)
    
    
    
    for path in paths:
        if debugMode:
            print(path)
        print(str(searcher.convertToArticleName(path[0])) + "  ->  " + str(searcher.convertToArticleName(path[-1])))
        #try:
        #    searchedPaths = searcher.bidirectionalSearcher(path[0], path[-1])
            #print("Shortest paths:")
        #    for a in searchedPaths:
        #        print(a[0])
        #except RuntimeError as e:
        #    print(e)
            
        #print("==========================")

    