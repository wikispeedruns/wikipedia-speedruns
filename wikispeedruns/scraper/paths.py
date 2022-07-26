import random

from db import get_db
from pymysql.cursors import DictCursor

import time

from typing import List, Dict, Any, Tuple

from .util import getLinks, convertToArticleName, convertPathToNames, convertToID

def bidirectionalSearcher(start: int, end:int) -> List[List[int]]:
    """High level logic for bidirectional search. Continuously calls forward and reverse search until an intersection is found,
    then traces the paths back to generate a concatenated final path.

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

    c = 0
    batchSize = 200    #Can be increased to reduce number of SQL queries

    pages = []
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
        pages.append(pageTitle)
        c += 1


    #Try getting the links of the pages marked to be processed
    links = getLinks(pages, forward = True)

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

    c = 0
    batchSize = 200   #Can be increased to reduce number of SQL queries

    pages = []
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
        pages.append(pageTitle)
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

