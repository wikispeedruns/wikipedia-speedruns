import pymysql
import time

db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor(pymysql.cursors.DictCursor)

start_time = time.time()

mapInsertQuery = "INSERT INTO `articleid` (`articleID`, `name`) VALUES (%s, %s);" 
edgesInsertQuery = "INSERT INTO `edgeidarticleid` (`src`, `dest`) VALUES (%s, %s);" 
getRowQuery = "SELECT * FROM edges where edgeID > %s AND edgeID < %s LIMIT 0, 10000"

articleMap = {}

articleCount = 1


def checkArticle(name):
    
    global articleCount
    
    #print(name)
    if not name in articleMap:
        articleMap[name] = articleCount
        articleCount += 1
    
    return articleMap[name] 


def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


if __name__ == "__main__":
    
    
    start_time = time.time()
    batchCount = 0
    
    cur.execute(
    '''
    DROP TABLE `articleid`
    '''
    )
    db.commit()

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS `articleid` (
            `articleID` INT NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`articleID`)
        );
        '''
    )
    db.commit()
    
    cur.execute(
    '''
    DROP TABLE `edgeidarticleid`
    '''
    )
    db.commit()

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS `edgeidarticleid` (
            `edgeID` INT NOT NULL AUTO_INCREMENT,
            `src` INT NOT NULL,
            `dest` INT NOT NULL,
            PRIMARY KEY (`edgeID`)
        );
        '''
    )
    db.commit()
    
    queryString = "SELECT max(edgeID) FROM edges;"
    cur.execute(queryString)
    maxID = int(cur.fetchall()[0]['max(edgeID)'])
    
    curID = 0
    batchSize = 500
    
    
    
    while curID < maxID:

        batchOutput = []

        cur.execute(getRowQuery, (str(curID), str(curID + batchSize)))
        queryResults = cur.fetchall()
        curID += batchSize

        
        for edge in queryResults:
            
            srcid = checkArticle(edge['src'])
            destid = checkArticle(edge['dest'])
            
            batchOutput.append((str(srcid), str(destid)))
                
                 
            
        batchCount += 1
        
        #print("Batch: " + str(batchCount) + ", articles: " + str(articlesCount)+", links: "+str(linksCount))
        
        cur.executemany(edgesInsertQuery, batchOutput)
        db.commit()
        
        if batchCount % 100 == 0:
            print(batchCount, articleCount)
    
    
    print("Done converting to int, now writing edge map")
    
    batchSize = 500
    keys = list(articleMap.keys())
    
    while len(keys) > 0:
        
        batchOutput = []
        
        n = min(batchSize, len(keys))
        
        for i in range(n):
            
            key = keys.pop()
            batchOutput.append((str(articleMap[key]), key))
            
        cur.executemany(mapInsertQuery, batchOutput)
        db.commit()
        
        
    db.close()
    
    elapsed_time = time.time() - start_time
    
    print("Read DB time: {}".format(hms_string(elapsed_time)))