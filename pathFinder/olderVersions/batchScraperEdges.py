import pymysql
import time

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

maxLength = 5   
            
def bfs(start, end):
    
    count = 0
    queue = [start]
    visited = {start : (None, 0)}

    batchSize = 200
    
    while queue:
        
        c = 0
        pages = {}
        startingDepth = 0
        while queue and c < batchSize:
            pageTitle = queue.pop(0)
            if c == 0:
                startingDepth = visited[pageTitle][1]
                print("Depth reached: " + str(visited[pageTitle][1] + 1))
            elif visited[pageTitle][1] != startingDepth:
                #print("Depth reached: " + str(visited[pageTitle][1] + 1))
                queue.insert(0, pageTitle)
                break
            
            pages[pageTitle] = True
            c += 1
        
        links = getLinks(pages, visited)
        
        for title in links:
                
            for link in links[title]:
            
                if link == end:
                    path = tracePath(visited, title, start)
                    path.append(link)
                    print("Articles checked: " + str(count))
                    print("Path length: " + str(len(path) - 1) + " clicks")
                    return path
            
            
                if link not in visited:
                    visited[link] = (title, visited[title][1] + 1)
                    queue.append(link)
                
                    count += 1
                    
                    if count % 10000 == 0:
                        print(str(count) +"," +str(tracePath(visited, link, start)))
                    
        
        


def tracePath(a, page, start):
    output = []
    cur = page
    while cur != start:
        output.append(cur)
        cur = a[cur][0]
    output.append(start)
    
    return Reverse(output)

def Reverse(lst):
    return [ele for ele in reversed(lst)]      

def batchQuery(queryString, arr):
    format_strings = ','.join(['%s'] * len(arr))
    cur.execute(queryString % format_strings,tuple(arr))
    return cur.fetchall()

def getLinks(pages, visited):
    
    queryString = "SELECT * FROM edges WHERE src IN (%s)"
    queryResults = batchQuery(queryString, list(pages.keys()))
    
    
    output = {}
    
    for queryEntry in queryResults:
            title = queryEntry['src']
            if title in pages:
                
                if title not in output:
                    output[title] = [queryEntry['dest']]
                else:
                    output[title].append(queryEntry['dest'])
        
    return output



startTitle = "William Howe, 5th Viscount Howe"
endTitle = "Graphical user interface"


start_time = time.time()

try:
    print(bfs(startTitle, endTitle))
except OverflowError:
    print("Exceeded max edge count")
    
print("Elapsed time:" + str(time.time() - start_time))