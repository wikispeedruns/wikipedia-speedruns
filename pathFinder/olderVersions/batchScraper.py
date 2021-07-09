import pymysql
import time
import pickle

redirects = pickle.load(open("redirects.p", "rb"))

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

maxLength = 5   
            
def bfs(start, end):
    
    count = 0
    queue = [start]
    visited = {}

    batchSize = 200
    
    while queue:
        
        c = 0
        pages = {}
        while queue and c < batchSize:
            pages[queue.pop(0)] = True
            c += 1
        
        titles, links = getLinks(pages, visited)
        
        for i in range(len(titles)):
                
            for link in links[i]:
            
                if link == end:
                    path = tracePath(visited, titles[i], start)
                    path.append(link)
                    print("Articles checked: " + str(count))
                    print("Path length: " + str(len(path) - 1) + " clicks")
                    return path
            
            
                if link not in visited:
                    visited[link] = titles[i]
                    queue.append(link)
                
                    count += 1
                    
                    if count % 10000 == 0:
                        print(str(count) +"," +str(tracePath(visited, link, start)))
                    
                    
                    
        
        


def tracePath(a, page, start):
    output = []
    cur = page
    while cur != start:
        output.append(cur)
        cur = a[cur]
    output.append(start)
    
    
    return Reverse(output)

def Reverse(lst):
    return [ele for ele in reversed(lst)]      

def replaceInArr(arr, new, old):
    return [new if x==old else x for x in arr]

def checkLinks(arr):
    for i in range(len(arr)):
        if arr[i] in redirects:
            arr[i] = redirects[arr[i]]
    return arr

def batchQuery(arr, queryString):
    format_strings = ','.join(['%s'] * len(arr))
    cur.execute(queryString % format_strings,tuple(arr))
    return cur.fetchall()

def getLinks(pages, visited):
    
    queryString = "SELECT title, links FROM pages WHERE title IN (%s)"
    queryResults = batchQuery(list(pages.keys()), queryString)
    
    
    outputTitles = []
    outputLinks = []
    
    for queryEntry in queryResults:
            title = queryEntry['title']
            if title in pages:
                outputTitles.append(queryEntry['title'])
                outputLinks.append(checkLinks(queryEntry['links'].split('||')))
        
    return outputTitles, outputLinks

startTitle = "William Howe, 5th Viscount Howe"
endTitle = "Graphical user interface"


start_time = time.time()

try:
    print(bfs(startTitle, endTitle))
except OverflowError:
    print("Exceeded max edge count")
    
print("Elapsed time:" + str(time.time() - start_time))