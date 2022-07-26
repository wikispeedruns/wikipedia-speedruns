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
        # If used in forward search, search will be based on outgoing edges. Incoming edges for reverse search
        if forward:
            query = "SELECT src AS cur, dst AS next FROM " + EDGE_TABLE + " WHERE src=%s"
        else:
            query = "SELECT dst AS cur, src AS next FROM " + EDGE_TABLE + " WHERE dst=%s"

        cur.execute(query, f"({','.join(pages)})")
        results = cur.fetchall()

        # Build the output dict, storing a list of dest links as the value:
        for row in results:
            cur_title = row['cur']
            next_title = row['next']

            output[cur_title].append(next_title)

        return output


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

