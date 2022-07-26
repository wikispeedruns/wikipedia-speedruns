import random

from db import get_db
from pymysql.cursors import DictCursor


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