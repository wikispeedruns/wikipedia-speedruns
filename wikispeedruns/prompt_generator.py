from wikispeedruns.scraper_graph_utils import getLinks, convertToArticleName, numLinksOnArticle, randomFilter, countWords, getRandomArticle, traceFromStart
import random


def checkSports(title):
        
    sportsKeywords = ["League", "season", "football", "rugby", "Championship", "baseball", "basketball", "Season", "Athletics", "Series", "Olympics", "Tennis", "Grand Prix"]
    
    try:
        year = int(title[0:4])
        if year > 1900:
            for word in sportsKeywords:
                if word in title:
                    return True
    except ValueError:
        return False

    return False



def checkStart(start, thresholdStart):
    
    title = convertToArticleName(start)
    
    if len(title) > 7:
        if title[0:7] == "List of":
            return False
    
    x = countWords(title)
    
    if randomFilter(True, 0.0047 *x*x*x - 0.0777*x*x + 0.2244*x + 1.226):
        #print("Random filtered:",start)
        return False
    
    if randomFilter(checkSports(title), 0.1):
        #print("Sports filtered:",start)
        return False
    
    if numLinksOnArticle(start) < thresholdStart:
        return False
    
    return True



def checkEnd(end, thresholdEnd):
    
    title = convertToArticleName(end)
    
    if len(title) > 7:
        if title[0:7] == "List of":
            return False
    
    x = countWords(title)
    
    if randomFilter(True, 0.0047 *x*x*x - 0.0777*x*x + 0.2244*x + 1.226):
        #print("Random filtered:",end)
        return False
    
    if randomFilter(checkSports(title), 0.05):
        #print("Sports filtered:",end)
        return False
    
    if numLinksOnArticle(end) < thresholdEnd:
        return False
    
    return True


def generatePrompts(thresholdStart=100, thresholdEnd=100, n=20, dist=15):
    
    generatedPromptPaths = []    
    
    print("Generating " + str(n) + " prompts")
    
    
    startGenerator = randStart(thresholdStart)
    endGenerator = randStart(thresholdEnd)
    
    while len(generatedPromptPaths) < n:
        
        sample = traceFromStart(startGenerator.__next__(), dist)
        
        if checkEnd(sample[-1], thresholdEnd) and len(sample) == dist + 1:
            generatedPromptPaths.append(sample)
            print(sample)
        
        #generatedPromptPaths.append([startGenerator.__next__(), endGenerator.__next__()])
        
    print("Finished generating prompts: \n")
    
    return generatedPromptPaths




def randStart(thresholdStart):
    
    generator = getRandomArticle()
    
    while True:
        start = generator.__next__()
        if checkStart(start, thresholdStart):
            yield start
        
        
        
        
        
