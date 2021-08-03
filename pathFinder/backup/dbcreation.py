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

def linkExtractor(text, id):
    
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


def linksToString(links):
    output = ""
    count = 0
    
    
    if len(links) > 0:
        output = output + links[0]
        count += 1
    while count < len(links):
        output = output + "||" + links[count]
        count += 1
    
    return output

def checkTitle(title):
    if title == "":
        raise ValueError("Empty Title")
    
    filteredPrefixes = ["Wikipedia:", "Portal:", "Template:", "MediaWiki:", "Draft:", "TimedText:", "File:", "Module:", "Image:"]
    for prefix in filteredPrefixes:
        if title.find(prefix) == 0:
            raise ValueError("Filtered Namespace")


db = pymysql.connect(host="localhost", user="root", password="9EEB00@@", database="testDB")
cur = db.cursor()

cur.execute(
    '''
    DROP TABLE `pages`
    '''
)
db.commit()

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS `pages` (
        `id` INT NOT NULL,
        `title` VARCHAR(255) NOT NULL,
        `redirect` VARCHAR(255) NOT NULL,
        `links` TEXT(65535) NOT NULL,
        PRIMARY KEY (`id`)
    );
    '''
)
db.commit()


pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)

totalCount = 0
articleCount = 0
redirectCount = 0
templateCount = 0
errorPagesCount = 0
skippedPagesCount = 0
errorPages = []
title = None
start_time = time.time()

pageQuery = "INSERT INTO `pages` (`id`, `title`, `redirect`, `links`) VALUES (%s, %s, %s, %s);"


error = False
skip = False

for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
    tname = strip_tag_name(elem.tag)
    
    

    if event == 'start':
        if tname == 'page':
            title = ''
            id = -1
            redirect = ''
            inrevision = False
            articleText = ''
        elif tname == 'revision':
            # Do not pick up on revision id's
            inrevision = True
            
            
    else:
        if tname == 'title':
            title = elem.text
            
            try:
                checkTitle(title)
            except ValueError as err:
                skip = True
                skippedPagesCount += 1
                print("Skipping article: "+title)
            else:
                skip = False
                
        elif not error and not skip:        
            
            if tname == 'id' and not inrevision:
                id = int(elem.text)
            elif tname == 'redirect':
                redirect = elem.attrib['title']
            elif tname == 'text':
                #print(title + ",ID:"+str(id))
                
                try:
                    articleText = linksToString(list(linkExtractor(elem.text, id)))
                except TimeoutError as err:
                    print(err)
                
                except:
                    errorPagesCount += 1
                    errorPages.append(title)
                    print("Parser Error at: " + title)
                    error = True
                else:
                    error = False
                    
            elif tname == 'page':
                totalCount += 1
                
                    
                if len(redirect) > 0:
                    redirectCount += 1
                    
                    try:
                        cur.execute(pageQuery, (str(id), title, redirect, ""))
                    except:
                        errorPagesCount += 1
                        errorPages.append(title)
                        print("SQL Error at: " + title)
                    
                else:
                    articleCount += 1
                    
                    try:
                        cur.execute(pageQuery, (str(id), title, "", articleText))
                    except:
                        errorPagesCount += 1
                        errorPages.append(title)
                        print("SQL Error at: " + title)
            
                if totalCount > 1 and (totalCount % 10000) == 0:
                    print("{:,}".format(totalCount))
                    print("Commiting to storage")
                    db.commit()

        elem.clear()

print("creating sorted index")

cur.execute(
    '''
        create index titleIndex on pages (title)
    '''
)
db.commit()

elapsed_time = time.time() - start_time

print("Total pages: {:,}".format(totalCount))
print("Template pages: {:,}".format(templateCount))
print("Article pages: {:,}".format(articleCount))
print("Redirect pages: {:,}".format(redirectCount))
print("Skipped pages: {:,}".format(skippedPagesCount))
print("Error pages: {:,}".format(errorPagesCount))
#print(errorPages)
print("Elapsed time: {}".format(hms_string(elapsed_time)))


db.commit()
db.close()