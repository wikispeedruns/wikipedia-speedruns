from abc import ABC, abstractmethod
from wikipedia2vec import Wikipedia2Vec

import pymysql
from pymysql.cursors import DictCursor

import requests

# TODO make these context proveriders?
class GraphProvider(ABC):
    '''
    Provide the outgoing links and other operations on the Wikipedia graph
    '''

    @abstractmethod
    def get_links(self, article):
        pass
    
    def get_links_batch(self, articles):
        return [self.get_links(a) for a in articles]


class APIGraph(GraphProvider):
    '''
    Graph queries served by the public Wikipedia API
    '''
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "pllimit": "max"
    }

    def __init__(self):
        pass

    def _links_from_resp(self, resp):
        links = list(resp["query"]["pages"].values())[0]["links"]
        links = [link["title"] for link in links]
        return list(filter(lambda title: ":" not in title, links))

    def get_links(self, article):
        resp = requests.get(self.URL, params={**self.PARAMS, "titles": article}).json() 
        return self._links_from_resp(resp)

    def get_links_batch(self, articles):
        # TODO figure out what happens if this returns too much
        resp = requests.get(url, params={**self.PARAMS, "titles": "|".join(articles)}).json()
        return self._links_from_resp(resp) 


class SQLGraph(GraphProvider):
    '''
    Graph queries served by the custom wikipedia speedruns SQL database graph
    '''
    def __init__(self, host, user, password, database):
        self.db = pymysql.connect(host=host, user=user, password=password, database=database)
        self.cursor = self.db.cursor(cursor=DictCursor)

    def get_links(self, article):
        id_query = "SELECT * FROM articleid WHERE name=%s"
        edge_query = """
            SELECT a.name FROM edgeidarticleid AS e 
            JOIN articleid AS a
            ON e.dest = a.articleID
            WHERE e.src = %s
        """
        self.cursor.execute(id_query, article)
        article_id = self.cursor.fetchone()["articleID"]
        if article_id is None: return None
        
        self.cursor.execute(edge_query, article_id)
        
        return [row["name"] for row in self.cursor.fetchall()]
        
    # TODO write a query that does this properly 
    #def get_links_batch(self, articles):
