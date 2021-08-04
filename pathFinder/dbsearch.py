import pymysql

def batchQuery(queryString, arr, cur):
    format_strings = ','.join(['%s'] * len(arr))
    cur.execute(queryString % format_strings,tuple(arr))
    return cur.fetchall()

def getLinks(pages, cur, forward = True):

    output = {}
    
    if forward:
        queryString = "SELECT * FROM edges WHERE src IN (%s)"
        queryResults = batchQuery(queryString, list(pages.keys()), cur)
        
        for queryEntry in queryResults:
            title = queryEntry['src']
            if title in pages:
                
                if title not in output:
                    output[title] = [(queryEntry['dest'], queryEntry['edgeID'])]
                else:
                    output[title].append((queryEntry['dest'], queryEntry['edgeID']))
                    
    else:
        queryString = "SELECT * FROM edges WHERE dest IN (%s)"
        queryResults = batchQuery(queryString, list(pages.keys()), cur)
        
        for queryEntry in queryResults:
            title = queryEntry['dest']
            if title in pages:
                
                if title not in output:
                    output[title] = [(queryEntry['src'], queryEntry['edgeID'])]
                else:
                    output[title].append((queryEntry['src'], queryEntry['edgeID']))
        
    return output



def getSrc(edgeID, cur):
    queryString = "SELECT src FROM edges WHERE edgeID=%s"
    cur.execute(queryString, str(edgeID))
    output = cur.fetchall()
    
    if len(output)>0:
        return output[0]['src']