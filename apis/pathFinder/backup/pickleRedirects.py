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


db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

redirectPagesCount = 0
batchCount = 0
start_time = time.time()

queryString = "SELECT max(id) FROM pages;"
cur.execute(queryString)
maxID = int(cur.fetchall()[0]['max(id)'])

getRowQuery = "SELECT * FROM pages where id > %s AND id < %s LIMIT 0, 10000"

curID = 0
batchSize = 500

redirects = {}

while curID < maxID:

    cur.execute(getRowQuery, (str(curID), str(curID + batchSize)))
    queryResults = cur.fetchall()
    curID += batchSize

    
    for page in queryResults:
        
        if page['redirect'] != '':
            
            redirects[page['title']] = page['redirect']
            
            redirectPagesCount += 1
        
    batchCount += 1
    
    if redirectPagesCount % 1000 == 0:
        print(str(batchCount) + "," + str(redirectPagesCount))
        
    #if batchCount > 10000:
    #    break

db.close()
      
elapsed_time = time.time() - start_time
print("Read DB time: {}".format(hms_string(elapsed_time)))
print("Redirect pages: {:,}".format(redirectPagesCount))

start_time = time.time()

pickle.dump(redirects, open("redirects.p","wb"))


elapsed_time = time.time() - start_time
print("Pickle time: {}".format(hms_string(elapsed_time)))
print("pickled size: " + str(os.path.getsize("redirects.p")*9.537*0.0000001)+"MB")
