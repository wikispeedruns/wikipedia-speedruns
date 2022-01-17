
import random

from db import get_db
from pymysql.cursors import DictCursor

import time

#from multiprocessing import Pool, TimeoutError

SCRAPER_DB = "scraper_graph"
ARTICLE_TABLE = SCRAPER_DB + ".articleid"
EDGE_TABLE = SCRAPER_DB + ".edgeidarticleid"

def batchQuery(queryString, arr, cur):
    format_strings = ','.join(['%s'] * len(arr))
    cur.execute(queryString % format_strings,tuple(arr))
    return cur.fetchall()


def getLinks(pages, forward = True):

    output = {}
    
    with get_db().cursor(cursor=DictCursor) as cur:
        if forward:
            queryString = "SELECT * FROM " + EDGE_TABLE + " WHERE src IN (%s)"
            #queryString = "SELECT * FROM edges WHERE src IN (%s)"
            queryResults = batchQuery(queryString, list(pages.keys()), cur)
            
            for queryEntry in queryResults:
                title = queryEntry['src']
                if title in pages:
                    
                    if title not in output:
                        output[title] = [(queryEntry['dest'], queryEntry['edgeID'])]
                    else:
                        output[title].append((queryEntry['dest'], queryEntry['edgeID']))
                        
        else:
            queryString = "SELECT * FROM " + EDGE_TABLE + " WHERE dest IN (%s)"
            queryResults = batchQuery(queryString, list(pages.keys()), cur)
            
            for queryEntry in queryResults:
                title = queryEntry['dest']
                if title in pages:
                    
                    if title not in output:
                        output[title] = [(queryEntry['src'], queryEntry['edgeID'])]
                    else:
                        output[title].append((queryEntry['src'], queryEntry['edgeID']))
            
        return output



def getSrc(edgeID, cur):
    queryString = "SELECT src FROM " + EDGE_TABLE + " WHERE edgeID=%s"
    #queryString = "SELECT src FROM edges WHERE edgeID=%s"
    cur.execute(queryString, str(edgeID))
    output = cur.fetchall()
    
    if len(output)>0:
        return output[0]['src']



def bidirectionalSearcher(start, end):
    forwardVisited = {start : (None, 0, 0)}
    reverseVisited = {end : (None, 0, 0)}

    forwardQueue = [start]
    reverseQueue = [end]
    
    while True:
        a = forwardBFS(start, end, forwardVisited, reverseVisited, forwardQueue)

        b = None
        if a != end:
            b = reverseBFS(start, end, forwardVisited, reverseVisited, reverseQueue)
        
        if a or b:
            
            if a and b:
                aPath = traceBidirectionalPath(a, start, end, forwardVisited, reverseVisited)
                bPath = traceBidirectionalPath(b, start, end, forwardVisited, reverseVisited)
                if len(aPath[0]) > len(bPath[0]):
                    a = None
                else:
                    b = None
                    
            if a:
                return [traceBidirectionalPath(a, start, end, forwardVisited, reverseVisited)]
            else:
                return [traceBidirectionalPath(b, start, end, forwardVisited, reverseVisited)]
            
            
            


def forwardBFS(start, end, forwardVisited, reverseVisited, queue):
    
    global articleCount
    
    c = 0
    batchSize = 200
    
    pages = {}
    startingDepth = 0

    #print(queue)

    if not queue:
        raise RuntimeError('No Path')
    
    while queue and c < batchSize:
        pageTitle = queue.pop(0)
        if c == 0:
            startingDepth = forwardVisited[pageTitle][1]
        elif forwardVisited[pageTitle][1] != startingDepth:
            queue.insert(0, pageTitle)
            break
        
        pages[pageTitle] = True
        c += 1
    
    try:
        links = getLinks(pages, forward = True)
    except:
        return None
    
    for title in links:
            
        for linkTuple in links[title]:
        
            link = linkTuple[0]
            edgeID = linkTuple[1]
            
            
            if link == end:
                print("Found end in forward search")
                forwardVisited[link] = (title, forwardVisited[title][1] + 1, edgeID)
                return link
            
        
            if link in reverseVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1, edgeID)
                return link
        
        
            if link not in forwardVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1, edgeID)
                queue.append(link)
                                    
    return None  



def reverseBFS(start, end, forwardVisited, reverseVisited, queue):
    
    global reverseArticleCount
    
    c = 0
    batchSize = 1
    
    pages = {}
    startingDepth = 0

    if not queue:
        raise RuntimeError('No Path')
    
    
    while queue and c < batchSize:
        pageTitle = queue.pop(0)
        if c == 0:
            startingDepth = reverseVisited[pageTitle][1]
        elif reverseVisited[pageTitle][1] != startingDepth:
            queue.insert(0, pageTitle)
            break
        
        pages[pageTitle] = True
        c += 1
    
    try:
        links = getLinks(pages, forward = False)
    except:
        return None
    
    for title in links:
            
        for linkTuple in links[title]:
        
            link = linkTuple[0]
            edgeID = linkTuple[1]
            
            
            if link == start:
                print("Found start in reverse search")
                reverseVisited[link] = (title, reverseVisited[title][1] + 1, edgeID)
                return link
            
            if link in forwardVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1, edgeID)
                return link
        
        
            if link not in reverseVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1, edgeID)
                queue.append(link)
                                
    return None      
        
        
def traceBidirectionalPath(intersection, start, end, forwardVisited, reverseVisited):
    forwardPath = tracePath(forwardVisited, intersection, start)
    reversePath = Reverse(tracePath(reverseVisited, intersection, end))
    
    forwardIDs = []
    for node in forwardPath:
        forwardIDs.append(forwardVisited[node][2])

    reverseIDs = []
    for node in reversePath:
        reverseIDs.append(reverseVisited[node][2])

    return (forwardPath + reversePath[1:], forwardIDs[1:] + reverseIDs[:-1])
    

def tracePath(visited, page, start):
    output = []
    cur = page
    while cur != start:
        output.append(cur)
        cur = visited[cur][0]
    
    output.append(start)
    
    return Reverse(output)

def Reverse(lst):
    return [ele for ele in reversed(lst)]      


def convertToID(name):
    with get_db().cursor(cursor=DictCursor) as cur: 
        queryString = "SELECT articleID from " + ARTICLE_TABLE + " where name=%s"
        cur.execute(queryString, str(name))
        output = cur.fetchall()

        if len(output) > 0:
            return output[0]['articleID']
        else:
            raise ValueError(f"Could not find article with name: {name}")
    
    
def convertToArticleName(id):
    
    with get_db().cursor(cursor=DictCursor) as cur: 
        queryString = "SELECT * from " + ARTICLE_TABLE + " where articleID=%s"
        cur.execute(queryString, str(id))
        output = cur.fetchall()

        if len(output)>0:
            return output[0]['name']
        else:
            raise ValueError(f"Could not find article with id: {id}")
    
def convertPathToNames(idpath):
    output = []
    for item in idpath:
        output.append(convertToArticleName(item))
        
    return output

def findPaths(startTitle, endTitle):
    
      
    start_time = time.time()
    
    startID = int(convertToID(startTitle))
    endID = int(convertToID(endTitle))
    
    
    #try:
    paths = bidirectionalSearcher(startID, endID)
    
    print(paths)
    
    for path in paths:
        print("Path:")
        print(path[0])
        print(convertPathToNames(path[0]))
        
    
    output = {"Articles":convertPathToNames(paths[0][0]),
              "ArticlesIDs":paths[0][0],
              "EdgeIDs": paths[0][1]}
    
    print(f"Search duration: {time.time() - start_time}")
    
    
    return output



def randStart(thresholdStart):
    
    with get_db().cursor(cursor=DictCursor) as cur:
        queryString = "SELECT max(edgeID) FROM " + EDGE_TABLE + ";"
        cur.execute(queryString)
        maxID = int(cur.fetchall()[0]['max(edgeID)'])
        
        while True:
            randIndex = random.randint(1, maxID)
            start = getSrc(randIndex, cur)
            if checkStart(start, thresholdStart):
                yield start
        
def checkStart(start, thresholdStart):
    
    title = convertToArticleName(start)
    
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
    
    title = convertToArticleName(end)
    
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
        
    links = getLinks({title:True}, forward=True)
        
    if title in links:
        links = links[title]
        
        return len(links)
        
    return 0

def traceFromStart(startTitle, dist):

    path = []
    
    currentTitle = startTitle
    while dist > 0:
        
        path.append(currentTitle)
        
        links = getLinks({currentTitle:True}, forward=True)
        
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
        
        if checkEnd(sample[-1], thresholdEnd) and len(sample) == dist + 1:
            generatedPromptPaths.append(sample)
            print(sample)
        
        #generatedPromptPaths.append([startGenerator.__next__(), endGenerator.__next__()])
        
    print("Finished generating prompts: \n")
    
    return generatedPromptPaths