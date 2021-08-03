# Simple example of streaming a Wikipedia 
# Copyright 2017 by Jeff Heaton, released under the The GNU Lesser General Public License (LGPL).
# http://www.heatonresearch.com
# -----------------------------
import xml.etree.ElementTree as etree
import codecs
import csv
import time
import os
import pymysql


start_time = time.time()

# http://www.ibm.com/developerworks/xml/library/x-hiperfparse/

PATH_WIKI_XML = 'C:\\Downloads'
FILENAME_WIKI = 'enwiki-20210601-pages-articles-multistream.xml'


# Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def strip_tag_name(t):
    t = elem.tag
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t

def getMainSections(text):
    initTime = time.time()
    
    start = 0
    while (time.time() - initTime) < 15:
        start = text.find("\n==", start)
        endInd = text.find("==\n", start)
        if start == -1 or endInd == -1:
            return
        encasedText = text[start+3:endInd].replace(" ", "")
        if len(encasedText) < 1:
            return
        
        if encasedText[0] != '=':
            yield [encasedText, start]
            
        start = endInd + 3
        
    raise TimeoutError("Inf loop in link extraction")
        
            
def deleteAfterSection(tag, text, sections):
    for section in sections:
        if tag == section[0] and section[1] < len(text):
            output = text[0:section[1]]
            return text[0:section[1]]
    return text

def deleteEncased(startMarker, endMarker, text):
    initTime = time.time()
    
    
    
    output = text
    while (time.time() - initTime) < 15:
        startInd = text.find(startMarker)
        endInd = text.find(endMarker)
        if startInd == -1 or endInd == -1:
            return output
        output = output[:startInd] + output[endInd + len(endMarker):]

    raise TimeoutError("Inf loop in link extraction")

def filterSections(text):
    
    sections = list(getMainSections(text))
    
    text = deleteAfterSection("References", text, sections)
    text = deleteAfterSection("Seealso", text, sections)
    text = deleteAfterSection("Furtherreading", text, sections)
    text = deleteAfterSection("Externallinks", text, sections)
    text = deleteAfterSection("Notesandreferences", text, sections)
    text = deleteAfterSection("Citations", text, sections)
    text = deleteAfterSection("Explanatorynotes", text, sections)
    text = deleteAfterSection("Notes", text, sections)
    
    text = deleteEncased("\n&lt;syntaxhighlight", "\n&lt;/syntaxhighlight&gt;", text)
    text = deleteEncased("\n&lt;!--", "\n--&gt;", text)
    
    return text

def linkExtractor(text):
    
    text = filterSections(text)
    initTime = time.time()
    
    start = 0
    while (time.time() - initTime) < 15:
        start = text.find("[[", start)
        endInd = text.find("]]", start)
        if start == -1 or endInd == -1:
            return
        encasedStart = text.find("[[", start + 2)
        if encasedStart != -1 and encasedStart < endInd:
            
            start = encasedStart
            
        linkText = checkLink(text[start + 2: endInd])
        
        if linkText is not None:
            yield linkText
         
        start = endInd + 2
        
    raise TimeoutError("Inf loop in link extraction")
        
def checkLink(link):
    
    output = link
    
    if len(output) == 0:
        return None
    if output.find("File:") != -1:
        return None
    else:
        a = link.find("|")
        if a == 0:
            return None
        elif a != -1:
            output = link[0:a]
    
    return output[0].upper() + output[1:]

def checkTitle(title):
    if title == "":
        raise ValueError("Empty Title")
    
    filteredPrefixes = ["Wikipedia:", "Portal:", "Template:", "MediaWiki:", "Draft:", "TimedText:", "File:", "Module:", "Image:"]
    for prefix in filteredPrefixes:
        if title.find(prefix) == 0:
            raise ValueError("Filtered Namespace")

def checkRedirects(arr, redirects):
    for i in range(len(arr)):
        if arr[i] in redirects:
            arr[i] = redirects[arr[i]]
    return arr

def log(msg):
    print(hms_string(start_time - time.time()) + ": " + msg)

def main():
    
    db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
    cur = db.cursor()

    start_time = time.time()
    
    log("Creating DB table")

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
    
    log("Finished creating DB table")
    
    pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)

    articleCount = 0
    redirectCount = 0
    linksCount = 0
    errorPagesCount = 0
    skippedPagesCount = 0
    errorPages = []
    title = None
    
    log("Creating redirect dictionary")

    redirects = {}

    error = False
    skip = False

    for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
        tname = strip_tag_name(elem.tag)

        if event == 'start':
            if tname == 'page':
                title = ''
                redirect = ''
                   
        else:
            if tname == 'title':
                title = elem.text
                
                try:
                    checkTitle(title)
                except ValueError as err:
                    skip = True
                    skippedPagesCount += 1
                    log("Skipping article: "+title)
                else:
                    skip = False
                    
            elif not error and not skip:        
                
                if tname == 'redirect':
                    redirect = elem.attrib['title']

                elif tname == 'page':
                        
                    if len(redirect) > 0:
                        redirectCount += 1
                        
                        try:
                            redirects[title] = redirect
                        except:
                            errorPagesCount += 1
                            errorPages.append(title)
                            log("Redirect error at: " + title)
                        
            elem.clear()
            
    log("Finished creating redirect dictionary")
    log("Starting article parsing & adding links to DB")
    
    error = False
    skip = False        
            
    insertQuery = "INSERT INTO `edges` (`src`, `dest`) VALUES (%s, %s);"        
            
    for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
        tname = strip_tag_name(elem.tag)

        if event == 'start':
            if tname == 'page':
                title = ''
                redirect = False
                linksOutput = []
                
                
        else:
            if tname == 'title':
                title = elem.text
                
                try:
                    checkTitle(title)
                except ValueError as err:
                    skip = True
                    skippedPagesCount += 1
                    log("Skipping article: "+title)
                else:
                    skip = False
                    
            elif not error and not skip:        
                
                if tname == 'redirect':
                    if len(elem.attrib['title']) > 0:
                        redirect = True
                elif tname == 'text':
                    
                    try:
                        linksOutput = checkRedirects(list(linkExtractor(elem.text, id)), redirects)
                    
                    except:
                        errorPagesCount += 1
                        errorPages.append(title)
                        log("Parser Error at: " + title)
                        error = True
                    else:
                        error = False
                        
                elif tname == 'page':
                        
                    if redirect == False:
                        articleCount += 1
                        
                        #need edit
                        
                        batchOutput = []
                        
                        for link in linksOutput:
                            if len(link) > 255:
                                log(str((title, link)))
                                continue
                            
                            batchOutput.append(title, link)
                            linksCount += 1
                        
                        try:
                            cur.executemany(insertQuery, batchOutput)
                            db.commit()
                        except:
                            errorPagesCount += 1
                            errorPages.append(title)
                            print("SQL Error at: " + title)
                            
                        if articleCount % 10000 == 0:
                            log(str(articleCount) + " articles, " + str(linksCount) + " links")
                        
                    #end edit

            elem.clear()
            
    log("Finished populating DB")

    log("Creating sorted indices for src")

    cur.execute(
        '''
            create index srcIndex on edges (src)
        '''
    )
    db.commit()

    log("Creating sorted indices for dest")

    cur.execute(
        '''
            create index destIndex on edges (dest)
        '''
    )
    db.commit()
    
    db.close()
    
    log("Finished creating sorting index")

    elapsed_time = time.time() - start_time

    print("Total links: {:,}".format(linksCount))
    print("Article pages: {:,}".format(articleCount))
    print("Redirect pages: {:,}".format(redirectCount))
    print("Skipped pages: {:,}".format(skippedPagesCount))
    print("Error pages: {:,}".format(errorPagesCount))
    #print(errorPages)
    print("Total Elapsed time: {}".format(hms_string(elapsed_time)))