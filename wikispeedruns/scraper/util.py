import random

from db import get_db
from pymysql.cursors import DictCursor

from typing import List, Dict, Any

#DB and table names for scraper
SCRAPER_DB = "scraper_graph"
ARTICLE_TABLE = SCRAPER_DB + ".articleid"
EDGE_TABLE = SCRAPER_DB + ".edgeidarticleid"

def getLinks(pages: List[int], forward: bool = True) -> Dict[int, List[int]]:
    """Gets the outgoing/incoming links of a list of articles as a batch query

    Args:
        pages (Dict[int, bool]): Dict, keys represent the article IDs that we want to find the links for
        forward (bool, optional): Direction of link. Defaults to True.

    Returns:
        Dict[int, List[int]]: Dict: key is the article ID, value is a list of article IDs that the key article is linked to
    """

    output = {p : [] for p in pages}


    with get_db().cursor(cursor=DictCursor) as cur:
        tuple_template = ','.join(['%s'] * len(pages))

        # If used in forward search, search will be based on outgoing edges. Incoming edges for reverse search
        if forward:
            query = f"SELECT src AS cur, dest AS next FROM {EDGE_TABLE} WHERE src IN ({tuple_template})"
        else:
            query = f"SELECT dest AS cur, src AS next FROM {EDGE_TABLE} WHERE dest IN ({tuple_template})"

        cur.execute(query, tuple(pages))
        results = cur.fetchall()

        # Build the output dict, storing a list of dest links as the value:
        for row in results:
            cur_title = row['cur']
            next_title = row['next']

            output[cur_title].append(next_title)

        return output


def convertToID(name: str) -> int:
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
    """Converts a path in the form of article IDs to article Titles"""
    output = []
    for item in idpath:
        output.append(convertToArticleName(item))

    return output

def numLinksOnArticle(title, forward = True):

    links = getLinks({title:True}, forward=forward)

    if title in links:
        links = links[title]

        return len(links)

    return 0


def countDigitsInTitle(title) :
    count = 0
    for character in title:
        if character.isdigit():
            count += 1
    return count


def randomFilter(bln, chance):
    if bln:
        if random.random() > chance:
            return True
    return False


def countWords(string):
    counter = 1
    for i in string:
        if i == ' ' or i == '-':
            counter += 1
    return counter



def getRandomArticle():
    with get_db().cursor() as cur:
        query = "SELECT max(articleID) FROM " + ARTICLE_TABLE + ";"
        cur.execute(query)
        (maxID, ) = cur.fetchone()

        while(True):
            yield random.randint(1, maxID)


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

        currentTitle = links[randIndex]

        dist -= 1

    return path + [currentTitle]


def convertNamePathToID(path):
    output = []
    for item in path:
        output.append(convertToID(item))
    return output



def articleLinkNumCheck(id, min_incoming, min_outgoing):
    num_incoming = numLinksOnArticle(id, forward = False)
    if num_incoming < min_incoming:
        return False, None, None

    num_outgoing = numLinksOnArticle(id)
    if num_outgoing < min_outgoing:
        return False, None, None

    return True, num_incoming, num_outgoing