import random

from typing import List, Any

from db import get_db

from .util import ARTICLE_TABLE
from .util import getLinks, convertToArticleName

def randStart(thresholdStart: int) -> Any:
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
