import scipy
from scipy.spatial import distance

# TODO base class

class MaxIterationsException(Exception):
    pass

class PathNotFoundException(Exception):
    pass


class GreedySearch:
    def __init__(self, embedding_provider, graph_provider, max_iterations=20):
        self.embeddings = embedding_provider
        self.graph = graph_provider
        self.max_iterations = max_iterations

    # Returns the next link to go to based on a greedy approach
    def get_next_greedy_link(self, start: str, end: str):
        min_dist = 2
        next_article = ""
        end_v = self.embeddings.get_embedding(end)

        for link in self.graph.get_links(start):    
            if (link == end): 
                return link
            try: 
                cur_v = self.embeddings.get_embedding(link)
            except KeyError:    
                continue
            dist = distance.cosine(cur_v, end_v)
            print(dist)
            if dist <= min_dist:
                next_article = link
                min_dist = dist

        if next_article == "":
            raise PathNotFoundException(f"GreedySearch: could not find path, current: {ret}")
        return next_article
    

    def search(self, start: str, end: str):
        # Greedily searches the wikipedia graph

        # Replace with this code to use the get_next_greedy_link helper function. 
        # Currently the original implementation is uncommented.
        # cur = start
        # ret = [start, ]

        # for i in range(self.max_iterations):
        #     next_article = get_next_greedy_link(cur, end)       
        #     ret.append(next_article)
        #     if(next_article == end):
        #         return ret
        #     cur = next_article

        # raise MaxIterationsException(f"GreedySearch: Max iterations {self.max_iterations} reached, current path: {ret}")

        cur = start
        end_v = self.embeddings.get_embedding(end)

        ret = [start, ]

        for i in range(self.max_iterations):
            min_dist = 2
            next_article = ""

            for link in self.graph.get_links(cur):    
                if link in ret:
                    continue

                if (link == end): 
                    #print(f"Found link in {cur}!")
                    ret.append(link)
                    return ret

                try: 
                    cur_v = self.embeddings.get_embedding(link)
                except KeyError:    
                    continue

                dist = distance.cosine(cur_v, end_v)

                if dist <= min_dist:
                    next_article = link
                    min_dist = dist

            if next_article == "":
                raise PathNotFoundException(f"GreedySearch: could not find path, current: {ret}")

            ret.append(next_article)
            cur = next_article

        raise MaxIterationsException(f"GreedySearch: Max iterations {self.max_iterations} reached, current path: {ret}")
        

class BeamSearch:
    def __init__(self, embedding_provider, graph_provider, max_iterations=20, width=10):
        self.embeddings = embedding_provider
        self.graph = graph_provider
        self.max_iterations = max_iterations
        self.width = width

    def _get_path(self, end, parent):
        ret = []
        cur = end
        while(parent[cur] != cur):
            ret.append(cur)
            cur = parent[cur]
        
        ret.append(cur)
        return list(reversed(ret))


    def search(self, start: str, end: str):
        # Define distance metric
        # TODO customizable
        end_v = self.embeddings.get_embedding(end)
        def get_dist(article):
            try: 
                cur_v = self.embeddings.get_embedding(link)
            except KeyError:    
                return 100
            return distance.cosine(cur_v, end_v)

        # Greedily searches the wikipedia graph
        cur_set = [start]
        # Keeps track of parent articles, also serves as visitor set
        parent = {start: start}

        for i in range(self.max_iterations):
            next_set = []
            for article in cur_set:
                outgoing = self.graph.get_links(article)
                for link in outgoing:
                    if link in parent:
                        continue
                    parent[link] = article
                    next_set.append((get_dist(link), link))

                    if link == end:
                        return self._get_path(link, parent)

            cur_set = [article for (_, article) in sorted(next_set)]
            cur_set = cur_set[:self.width]
            print(f"Articles in iteration {i}: ", cur_set)
        
        raise MaxIterationsException(f"BeamSearch: Max iterations {self.max_iterations} reached")
        
# TODO probabilistic search (for random results)
# TODO other heuristics
