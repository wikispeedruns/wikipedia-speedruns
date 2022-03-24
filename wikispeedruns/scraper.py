import random

from db import get_db
from pymysql.cursors import DictCursor

import time

from typing import List, Dict, Any, Tuple

#DB and table names for scraper
SCRAPER_DB = "scraper_graph"
ARTICLE_TABLE = SCRAPER_DB + ".articleid"
EDGE_TABLE = SCRAPER_DB + ".edgeidarticleid"



def batchQuery(queryString: str, arr: List[str], cur: Any) -> Dict[str, str]:
#def batchQuery(queryString, arr, cur):
    """batchQuery helper function"""
    format_strings = ','.join(['%s'] * len(arr))
    cur.execute(queryString % format_strings,tuple(arr))
    return cur.fetchall()


def getLinks(pages: Dict[int, bool], forward: bool = True) -> Dict[int, List[int]]:
#def getLinks(pages, forward):
    """Gets the outgoing/incoming links of a list of articles as a batch query

    Args:
        pages (Dict[int, bool]): Dict, keys represent the article IDs that we want to find the links for
        forward (bool, optional): Direction of link. Defaults to True.

    Returns:
        Dict[int, List[int]]: Dict: key is the article ID, value is a list of article IDs that the key article is linked to
    """

    output = {}

    with get_db().cursor(cursor=DictCursor) as cur:
        #If used in forward search, search will be based on outgoing edges. Incoming edges for reverse search
        if forward:

            #Gets the links for all batch queried article IDs.
            queryString = "SELECT * FROM " + EDGE_TABLE + " WHERE src IN (%s)"
            queryResults = batchQuery(queryString, list(pages.keys()), cur)
            
            #Iterate through each queried article
            for queryEntry in queryResults:
                title = queryEntry['src']
                if title in pages:
                    
                    #Build the output dict, storing a list of dest links as the value
                    if title not in output:
                        output[title] = [queryEntry['dest']]
                    else:
                        output[title].append(queryEntry['dest'])
                        
        else:
            queryString = "SELECT * FROM " + EDGE_TABLE + " WHERE dest IN (%s)"
            queryResults = batchQuery(queryString, list(pages.keys()), cur)
            
            for queryEntry in queryResults:
                title = queryEntry['dest']
                if title in pages:
                    
                    if title not in output:
                        output[title] = [queryEntry['src']]
                    else:
                        output[title].append(queryEntry['src'])
            
        return output



def bidirectionalSearcher(start: int, end:int) -> List[List[int]]:
#def bidirectionalSearcher(start, end):
    """High level logic for bidirectional search. Continuously calls forward and reverse search until an intersection is found, then traces the paths back to generate a concatenated final path.

    Args:
        start (int): starting article ID
        end (int): ending article ID

    Returns:
        List[int]: final concatenated path
    """
    #Initialize the visited dictionaries, and set the end and start predecesors to be None
    forwardVisited = {start : (None, 0)}
    reverseVisited = {end : (None, 0)}

    #add both article IDs to their respective queues
    forwardQueue = [start]
    reverseQueue = [end]
    

    #Iterate through: forward search first, reverse search second. Until an intersection has been found
    while True:
        #try to find an intersection in forward search (a page reverse search has visited before)
        #this function batch processes articles, but only those that are at the same depth/distance from start
        a = forwardBFS(start, end, forwardVisited, reverseVisited, forwardQueue)

        #do reverse search
        b = None
        if a != end:
            b = reverseBFS(start, end, forwardVisited, reverseVisited, reverseQueue)
        
        #if intersection was found for either search, trace the found
        if a or b:
            
            #if intesection is found for both searches, only check the path with shorter length
            if a and b:
                aPath = traceBidirectionalPath(a, start, end, forwardVisited, reverseVisited)
                bPath = traceBidirectionalPath(b, start, end, forwardVisited, reverseVisited)
                if len(aPath) > len(bPath):
                    a = None
                else:
                    b = None
            
            #trace the path using the forward search path
            if a:
                return [traceBidirectionalPath(a, start, end, forwardVisited, reverseVisited)]
            else:
                return [traceBidirectionalPath(b, start, end, forwardVisited, reverseVisited)]
            

def forwardBFS(start: int, end: int, forwardVisited: Dict[int, Tuple[int, int]], reverseVisited: Dict[int, Tuple[int, int]], queue: List[int]) -> int:
#def forwardBFS(start, end, forwardVisited, reverseVisited, queue):

    """Forward search component of the bidirectional search. Looks for any article that the reverse search component has previously visited,
    which makes it an intersection. The full path can then be traced from the intersection

    Args:
        start (int): starting article ID
        end (int): end article ID
        forwardVisited (Dict[int, tuple): dictionary for the visited components of the forward search. This function populates this dictionary.
        reverseVisited (Dict[int, tuple): dictionary for the visited components of the reverse search. Should not be modified here
        queue (List[int]): queue of articles to search through, only for forward search. Reverse search has its separate queue

    Raises:
        RuntimeError: If a path has not been found

    Returns:
        int: article ID of intersection if found.
    """

    global articleCount
    
    c = 0
    batchSize = 200    #Can be increased to reduce number of SQL queries
    
    pages = {}
    startingDepth = 0

    #CHeck if the queue is empty before a path is found
    if not queue:
        raise RuntimeError(f'No Path in forward for {start}, {end}')
    
    #pop from queue and prepare to process the first {batchSize} queue elements, however many is left in the queue, or however many elements if left in the queue that all has the same depth.
    #ensure that only elements of the same depth are searched in each function call
    while queue and c < batchSize:
        #pop page from queue
        pageTitle = queue.pop(0)

        #Check to see if the page is the same depth as the first processed page of the batch
        #if not, return the element to the queue and break loop
        if c == 0:
            startingDepth = forwardVisited[pageTitle][1]
        elif forwardVisited[pageTitle][1] != startingDepth:
            queue.insert(0, pageTitle)
            break

        #Mark a page to retrieve its links in this batch by batch query in SQL
        pages[pageTitle] = True
        c += 1
    

    #Try getting the links of the pages marked to be processed
    try:
        links = getLinks(pages, forward = True)
    except:
        return None

    #iterate through each batch article
    for title in links:
        #iterate through the outgoing links of each batch article            
        for link in links[title]:

            #FOR ALL: add article predecesor and depth to forwardVisited


            #check if any of the links is the startnig article
            # This would mean a length 1 path (no intersection was found)

            if link == end:
                print("Found end in forward search")
                forwardVisited[link] = (title, forwardVisited[title][1] + 1)
                return link
            
            #Check if a link has been previously visited by the reverse search.
            #If so, this means the link is an intersection of forward and reverse search, return the article ID of this intersection
            if link in reverseVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1)
                return link
        
            #If link was not previously visited in reverse search, append to queue
            if link not in forwardVisited:
                forwardVisited[link] = (title, forwardVisited[title][1] + 1)
                queue.append(link)

    #if no intersection was found in this batch                                
    return None  

def reverseBFS(start: int, end: int, forwardVisited: Dict[int, Tuple[int, int]], reverseVisited: Dict[int, Tuple[int, int]], queue: List[int]) -> int:
#def reverseBFS(start, end, forwardVisited, reverseVisited, queue):
    """Reverse search component of the bidirectional search. Looks for any article that the forward search component has previously visited,
    which makes it an intersection. The full path can then be traced from the intersection

    Args:
        start (int): starting article ID
        end (int): end article ID
        forwardVisited (Dict[int, tuple): dictionary for the visited components of the forward search. Should not be modified here
        reverseVisited (Dict[int, tuple): dictionary for the visited components of the reverse search. This function populates this dictionary.
        queue (List[int]): queue of articles to search through, only for reverse search. Forward search has its separate queue

    Raises:
        RuntimeError: If a path has not been found

    Returns:
        int: article ID of intersection if found.
    """
    
    global reverseArticleCount
    
    c = 0
    batchSize = 200   #Can be increased to reduce number of SQL queries
    
    pages = {}
    startingDepth = 0

    #CHeck if the queue is empty before a path is found
    if not queue:
        raise RuntimeError(f'No Path in reverse for {start}, {end}')
    
    #pop from queue and prepare to process the first {batchSize} queue elements, however many is left in the queue, or however many elements if left in the queue that all has the same depth.
    #ensure that only elements of the same depth are searched in each function call
    while queue and c < batchSize:
        #pop page from queue
        pageTitle = queue.pop(0)

        #Check to see if the page is the same depth as the first processed page of the batch
        #if not, return the element to the queue and break loop
        if c == 0:
            startingDepth = reverseVisited[pageTitle][1]
        elif reverseVisited[pageTitle][1] != startingDepth:
            queue.insert(0, pageTitle)
            break
        
        #Mark a page to retrieve its links in this batch by batch query in SQL
        pages[pageTitle] = True
        c += 1
    
    #Try getting the links of the pages marked to be processed
    try:
        links = getLinks(pages, forward = False)
    except:
        return None
    
    #iterate through each batch article
    for title in links:
            
        #iterate through the outgoing links of each batch article
        for link in links[title]:

            #FOR ALL: add article predecesor and depth to reverseVisited


            #check if any of the links is the startnig article
            # This would mean a length 1 path (no intersection was found)
            # ## SINCE REVERSE SEARCH FIRES AFTER FORWARD SEARCH, THIS SHOULD NEVER FIRE            
            if link == start:
                print("Found start in reverse search")
                reverseVisited[link] = (title, reverseVisited[title][1] + 1)
                return link
            
            #Check if a link has been previously visited by the forward search.
            #If so, this means the link is an intersection of forward and reverse search, return the article ID of this intersection
            if link in forwardVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1)
                return link
        
            #If link was not previously visited in forward search, append to queue
            if link not in reverseVisited:
                reverseVisited[link] = (title, reverseVisited[title][1] + 1)
                queue.append(link)

    #if no intersection was found in this batch
    return None      
        

def traceBidirectionalPath(intersection: int, start: int, end: int, forwardVisited: Dict[int, Tuple[int, int]], reverseVisited: Dict[int, Tuple[int, int]]) -> List[int]:
#def traceBidirectionalPath(intersection, start, end, forwardVisited, reverseVisited):

    """Once an intersection is found, use this function to trace back to the start and end pages on both directions using the visited dictionary, and return the concatenated full path

    Args:
        intersection (int): the intersection article ID that the bidirectional searcher found
        start (int): starting article ID of the search
        end (int): end article ID of the search
        forwardVisited (Dict[int, tuple): Dict containing the articles the forward search visited along with their predecesors and depth
        reverseVisited (Dict[int, tuple): ^ same but for the articles reverse search found

    Returns:
        List[int]: The final concatenated path found
    """
    forwardPath = tracePath(forwardVisited, intersection, start)
    reversePath = Reverse(tracePath(reverseVisited, intersection, end))
    return forwardPath + reversePath[1:]
    

def tracePath(visited: Dict[int, Tuple[int, int]], page: int, start: int) -> List[int]:
#def tracePath(visited, page, start):

    """Given a Dict of visited pages and the 'end' page. Trace back the visited path and return a list representing the visited path from start to end

    Args:
        visited (Dict): Visited dict, contains article id key to its predecesor and depth
        page (int): the end of the path (tracing back starts with this page)
        start (int): the start page of the path (tracing back ends with this page)

    Returns:
        List[int]: traced path starting with 'start' and ending with 'end'
    """
    output = []
    cur = page
    while cur != start:
        output.append(cur)
        cur = visited[cur][0]
    
    output.append(start)
    
    return Reverse(output)

def Reverse(lst: List[Any]) -> List[Any]:
#def Reverse(lst):
    """Reverses the elements of a list, for building the reverse search section of the path"""
    return [ele for ele in reversed(lst)]      


def convertToID(name: str) -> int:
#def convertToID(name):
    """Converts a single article title to its corresponding article id
    """
    with get_db().cursor(cursor=DictCursor) as cur: 
        queryString = "SELECT articleID from " + ARTICLE_TABLE + " where name=%s"
        cur.execute(queryString, str(name))
        output = cur.fetchall()

        if len(output) > 0:
            return output[0]['articleID']
        else:
            raise ValueError(f"Could not find article with name: {name}")
    
    
def convertToArticleName(id: int) -> str:
#def convertToArticleName(id):
    """Converts a single article ID to its corresponding article title
    """
    with get_db().cursor(cursor=DictCursor) as cur: 
        queryString = "SELECT * from " + ARTICLE_TABLE + " where articleID=%s"
        cur.execute(queryString, str(id))
        output = cur.fetchall()

        if len(output)>0:
            return output[0]['name']
        else:
            raise ValueError(f"Could not find article with id: {id}")
    
def convertPathToNames(idpath: List[int])-> List[str]:
#def convertPathToNames(idpath):
    """Converts a path in the form of article IDs to article Titles"""
    output = []
    for item in idpath:
        output.append(convertToArticleName(item))
        
    return output


def findPaths(startTitle: str, endTitle: str) -> Dict[str, List]:
#def findPaths(startTitle, endTitle):
    """given a start and end article title, find a single shortest path using bidirectional BFS search

    Args:
        startTitle (str): Title of the first article
        endTitle (str): Title of the second article

    Returns:
        Dict: {
            "Articles": List[str], article names of shortest path,
            "ArticleIDs": List[int], article IDs of shortest path
        }
    """
      
    start_time = time.time()
    
    if startTitle == endTitle:
        return {"Articles":[convertToArticleName(startTitle)],
              "ArticlesIDs":[endTitle]}
    
    startID = startTitle
    endID = endTitle
    if not id:
        startID = int(convertToID(startTitle))
        endID = int(convertToID(endTitle))
    
    #try:
    paths = bidirectionalSearcher(startID, endID)
    
    #print(paths)
    
    for path in paths:
        #print("Path:")
        #print(path)
        print(convertPathToNames(path))
        
    
    output = {"Articles":convertPathToNames(paths[0]),
              "ArticlesIDs":paths[0]}
    
    #print(f"Search duration: {time.time() - start_time}")
    
    
    return output

def randStart(thresholdStart: int) -> Any:
#def randStart(thresholdStart):
    """Generator for starting article

    Args:
        thresholdStart (int): Minimum number of outgoing links the article must have, passed to function

    Yields:
        Iterator[int]: the id of a valid starting article
    """
    
    with get_db().cursor() as cur:
        query = "SELECT max(articleID) FROM " + ARTICLE_TABLE + ";"
        cur.execute(query)
        (maxID, ) = cur.fetchone()
        
        while True:
            start  = random.randint(1, maxID)
            if checkStart(start, thresholdStart):
                yield start


def checkEnd(end: int, thresholdEnd: int) -> bool:
#def checkEnd(end, thresholdEnd):
    """Higher level checker function to determine whether or not a given end article is valid as the goal page of a randomly generated prompt

    Args:
        end (int): article ID of the checked article
        thresholdEnd (int): The number of outgoing links the article must have

    Returns:
        bool: Whether the article is valid
    """
    
    # convert article ID to string to check the title contents
    title = convertToArticleName(end)
    
    # eliminate all "List of" articles
    if len(title) > 7:
        if title[0:7] == "List of":
            return False
    
    #Count the number of words in the article title
    x = countWords(title)
    
    #Skew the filter against articles with more words with a somewhat logarithmic polynomial
    #The more words in the article, the lower the chance of being accepted
    if randomFilter(True, 0.0047 *x*x*x - 0.0777*x*x + 0.2244*x + 1.226):
        return False
    
    #Allow only a 5% chance of being accepted of the article is a specific sports season/team/game
    if randomFilter(checkSports(title), 0.05):
        return False
    
    #Check that the article has at least a threshold amount of outgoing links.
    if numLinksOnArticle(end) < thresholdEnd:
        return False
    
    return True        
        
def checkStart(start: int, thresholdStart: int) -> bool:
#def checkStart(start, thresholdStart):
    """Similar to checkEnd, with a higher tolerance for sports pages"""

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

def countWords(string: str) -> int:
#def countWords(string):
    """Count words in a string, used for skewing start and end filters against articles with longer titles"""
    counter = 1
    for i in string:
        if i == ' ' or i == '-':
            counter += 1
    return counter

def randomFilter(bln: bool, chance: float) -> bool:
#def randomFilter(bln, chance):

    """Pass a boolean through a RNG gate. Overall, {chance}% of True booleans will remain True

    Args:
        bln (bool): the original boolean
        chance (float): chance of the original boolean remaining as a True value

    Returns:
        bool: output result
    """
    if bln:
        if random.random() > chance:
            return True
    return False

def checkSports(title: str) -> bool:
#def checkSports(title):
    """Check to see if the article is a sports season/team page. If true, bias against these articles. 
    To be considered a sports season/team/game page, the article's first 4 characters must form a year > 1900, 
    and the article name must also contain one of the identified sports keywords.

    Args:
        title (str): Actual title of the article

    Returns:
        bool: If the article can be categorized as a sports related page
    """

    #Keywords to be iterated through, can continue expanding. 
    sportsKeywords = ["League", "season", "football", "rugby", "Championship", "baseball", "basketball", "Season", "Athletics", "Series", "Olympics", "Tennis", "Grand Prix"]
    
    try:
        #check that first 4 chars form a year
        year = int(title[0:4])
        if year > 1900:
            #check for any sports keyword
            for word in sportsKeywords:
                if word in title:
                    return True
    except ValueError:
        return False

    return False

def numLinksOnArticle(id : int) -> int:
#def numLinksOnArticle(id):
    """get the number of outgoing links of a given article

    Args:
        id (int): article id

    Returns:
        int: number of outgoing links
    """

    links = getLinks({id:True}, forward=True)
        
    if id in links:
        links = links[id]
        return len(links)
        
    return 0

def traceFromStart(startID: int, dist: int) -> List[int]:
#def traceFromStart(startID, dist):
    """helper function to trace a path from a given article number

    Args:
        startID (int): Starting article ID
        dist (int): distance to jump

    Returns:
        List[int]: resulting path as a list of visited article IDs
    """

    path = []
    currentTitle = startID

    while dist > 0:
        
        path.append(currentTitle)    
        links = getLinks({currentTitle:True}, forward=True)
        
        #Check that the getLinks function was actually able to retrieve the links of the article
        if currentTitle in links:
            links = links[currentTitle]
        else:
            break
        
        randIndex = random.randint(0, len(links) - 1)
        
        currentTitle = links[randIndex]
        
        dist -= 1
    
    return path + [currentTitle]

def generatePrompts(thresholdStart : int = 100, thresholdEnd : int = 100, n : int = 20, dist: int = 15) -> List[List[int]]:
#def generatePrompts(thresholdStart = 100, thresholdEnd = 100, n = 20, dist = 15):
    """Generates N random paths. THe function uses a random article generator to get a start article, traces a random path 'dist' steps away, 
    checks that the end article also fits the criteria, and appends the resulting path as a list to the output list. 

    Args:
        thresholdStart (int, optional): Number of outgoing links an article must have to be considered a valid start. Defaults to 100.
        thresholdEnd (int, optional): Number of outgoing links an article must have to be considered a vlid end. Defaults to 100.
        n (int, optional): Number of prompts to generate. Defaults to 20.
        dist (int, optional): How far to jump away for the end article. Defaults to 15.

    Returns:
        List[List]: list of random paths. 
    """
    
    generatedPromptPaths = []    
    
    print("Generating " + str(n) + " prompts")
    
    # start article generator
    startGenerator = randStart(thresholdStart)
    
    #generate n randomly traced and valid paths, each path uses a different start article
    while len(generatedPromptPaths) < n:
        
        sample = traceFromStart(startGenerator.__next__(), dist)
        
        if checkEnd(sample[-1], thresholdEnd) and len(sample) == dist + 1:
            generatedPromptPaths.append(sample)
            print(sample)
                
    print("Finished generating prompts: \n")
    
    return generatedPromptPaths
