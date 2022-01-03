# Simple example of streaming a Wikipedia 
# Copyright 2017 by Jeff Heaton, released under the The GNU Lesser General Public License (LGPL).
# http://www.heatonresearch.com
# -----------------------------
import time
import pymysql
import pickle
import os

# Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def checkLinks(arr):
    for i in range(len(arr)):
        if arr[i] in redirects:
            arr[i] = redirects[arr[i]]
    return arr

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

cur.execute(
    '''
    DROP TABLE `edges`
    '''
)
db.commit()

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS `edges` (
        `edgeID` INT NOT NULL AUTO_INCREMENT,
        `src` VARCHAR(255) NOT NULL,
        `dest` VARCHAR(255) NOT NULL,
        PRIMARY KEY (`edgeID`)
    );
    '''
)
db.commit()

linksCount = 0
articlesCount = 0
batchCount = 0
start_time = time.time()

queryString = "SELECT max(id) FROM pages;"
cur.execute(queryString)
maxID = int(cur.fetchall()[0]['max(id)'])

getRowQuery = "SELECT * FROM pages where id > %s AND id < %s LIMIT 0, 10000"
insertQuery = "INSERT INTO `edges` (`src`, `dest`) VALUES (%s, %s);"

curID = 0
batchSize = 500

redirects = pickle.load(open("redirects.p", "rb"))

while curID < maxID:

    batchOutput = []

    cur.execute(getRowQuery, (str(curID), str(curID + batchSize)))
    queryResults = cur.fetchall()
    curID += batchSize

    
    for page in queryResults:
        
        if page['redirect'] == '':
            
            links = checkLinks(page['links'].split('||'))
            
            for link in links:
                
                if len(link) > 255:
                    print((page['title'], link))
                    continue
                
                batchOutput.append((page['title'], link))
                linksCount += 1
        
            articlesCount += 1    
        
    batchCount += 1
    
    print("Batch: " + str(batchCount) + ", articles: " + str(articlesCount)+", links: "+str(linksCount))
        
    #if batchCount > 10:
    #    break
    
    cur.executemany(insertQuery, batchOutput)
    db.commit()

print("creating sorted indices")

cur.execute(
    '''
        create index srcIndex on edges (src)
    '''
)
db.commit()

cur.execute(
    '''
        create index destIndex on edges (dest)
    '''
)
db.commit()

db.close()
      
elapsed_time = time.time() - start_time
print("Read DB time: {}".format(hms_string(elapsed_time)))
print("Batches: {:,}".format(batchCount))
print("Pages: {:,}".format(articlesCount))
print("Links: {:,}".format(linksCount))
