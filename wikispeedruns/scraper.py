import time

from scraper_graph_utils import getLinks, convertToID, convertToArticleName



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
                if len(aPath) > len(bPath):
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
            
        for link in links[title]:
                    
            if link == end:
                print("Found end in forward search")
                forwardVisited[link] = (title, forwardVisited[title][1] + 1)
                return link
            
        
            if link in reverseVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1)
                return link
        
        
            if link not in forwardVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1)
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
            
        for link in links[title]:            
            if link == start:
                print("Found start in reverse search")
                reverseVisited[link] = (title, reverseVisited[title][1] + 1)
                return link
            
            if link in forwardVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1)
                return link
        
        
            if link not in reverseVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1)
                queue.append(link)
                                
    return None      
        
        
def traceBidirectionalPath(intersection, start, end, forwardVisited, reverseVisited):
    forwardPath = tracePath(forwardVisited, intersection, start)
    reversePath = Reverse(tracePath(reverseVisited, intersection, end))
    return forwardPath + reversePath[1:]
    

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
        print(path)
        print(convertPathToNames(path))
        
    
    output = {"Articles":convertPathToNames(paths[0]),
              "ArticlesIDs":paths[0]}
    
    print(f"Search duration: {time.time() - start_time}")
    
    
    return output


