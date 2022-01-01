import pymysql
import time
from .dbsearch import getLinks
from .dbcreation import log

debugMode = True
articleCount = 0
reverseArticleCount = 0

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

def bidirectionalSearcher(start, end):
    forwardVisited = {start : (None, 0, 0)}
    reverseVisited = {end : (None, 0, 0)}

    forwardQueue = [start]
    reverseQueue = [end]
    
    while True:
        a = forwardBFS(start, end, forwardVisited, reverseVisited, forwardQueue)
        
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
                if debugMode:
                    log("Found intersection!: \"" + str(a) + '\"\n')
                return [traceBidirectionalPath(a, start, end, forwardVisited, reverseVisited)]
            else:
                if debugMode:
                    log("Found intersection!: \"" + str(b) + '\"\n')
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
            if debugMode:
                log("Forward depth reached: " + str(forwardVisited[pageTitle][1] + 1))
        elif forwardVisited[pageTitle][1] != startingDepth:
            queue.insert(0, pageTitle)
            break
        
        pages[pageTitle] = True
        c += 1
    
    try:
        links = getLinks(pages, cur, forward = True)
    except:
        return None
    
    for title in links:
            
        for linkTuple in links[title]:
        
            link = linkTuple[0]
            edgeID = linkTuple[1]
        
            if link in reverseVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1, edgeID)
                return link
        
        
            if link not in forwardVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1, edgeID)
                queue.append(link)
            
                articleCount += 1
                
                if articleCount % 10000 == 0:
                    if debugMode:
                        log("Forward: " + str(tracePath(forwardVisited, link, start)) + ", " + str(articleCount))
                    
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
            if debugMode:
                log("Reverse depth reached: " + str(reverseVisited[pageTitle][1] + 1))
        elif reverseVisited[pageTitle][1] != startingDepth:
            queue.insert(0, pageTitle)
            break
        
        pages[pageTitle] = True
        c += 1
    
    try:
        links = getLinks(pages, cur, forward = False)
    except:
        return None
    
    for title in links:
            
        for linkTuple in links[title]:
        
            link = linkTuple[0]
            edgeID = linkTuple[1]
            
            if link in forwardVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1, edgeID)
                return link
        
        
            if link not in reverseVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1, edgeID)
                queue.append(link)
            
                reverseArticleCount += 1
                
                if reverseArticleCount % 10000 == 0:
                    if debugMode:
                        log("Reverse: " + str(tracePath(reverseVisited, link, end)) + ", " + str(reverseArticleCount))
                    
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
    queryString = "SELECT * from articleID where name=%s"
    cur.execute(queryString, str(name))
    output = cur.fetchall()
    
    if len(output)>0:
        return output[0]['articleID']
    
    
def convertToArticleName(id):
    queryString = "SELECT * from articleID where articleID=%s"
    cur.execute(queryString, str(id))
    output = cur.fetchall()
    
    if len(output)>0:
        return output[0]['name']
    
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
    
    if debugMode:
        print(paths)
    
    for path in paths:
        print("Path:")
        print(path[0])
        print(convertPathToNames(path[0]))
        if debugMode:
            print("DEBUG - EdgeID:")
            print(str(path[1]) + '\n')
            
    #except Exception as error:
    #    print(repr(error))

    if debugMode:
        print("Forward articles: " + str(articleCount))
        print("Reverse articles: " + str(reverseArticleCount))
        print("Total checked articles: " + str(articleCount + reverseArticleCount))
            
        print("Elapsed time:" + str(time.time() - start_time) + ' seconds\n')

    return paths

if __name__ == '__main__':
    
    debugMode = True

    start = "Candidates of the 1955 Australian federal election"
    end = "Leech"
    
    print(findPaths(start, end))



