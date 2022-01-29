import wikispeedruns.scraper_graph_utils as utils
import math

def getDifficultyScore(id, min_incoming, min_outgoing):
    
    num_incoming = utils.numLinksOnArticle(id, forward = False)
    if num_incoming < min_incoming:
        return -1, 0, 0, 0, 0
    
    num_outgoing = utils.numLinksOnArticle(id)
    if num_outgoing < min_outgoing:
        return -1, 0, 0, 0, 0
    
    title = utils.convertToArticleName(id)
    num_digits = utils.countDigitsInTitle(title)
    num_words = utils.countWords(title)
    
    incoming_score = 100 / (1 + math.exp(-0.04 * (num_incoming - min_incoming)))
    outgoing_score = 100 / (1 + math.exp(-0.04 * (num_outgoing - min_outgoing)))
    
    words_score = 0.7 * math.pow(num_words, 3) - 11.41 * math.pow(num_words, 2) + 41.2 * num_words + 48.67
    if num_words == 2:
        words_score * 0.5
    
    digits_score = 10
    if num_digits == 4 or num_digits == 0:
        digits_score = 50
        
    digits_weight = 2
    words_weight = 5
    incoming_weight = 8.5
    outgoing_weight = 10
    
    final_score = digits_weight * digits_score + words_score * words_weight + incoming_score * incoming_weight + outgoing_score * outgoing_weight
    
    return final_score, digits_weight * digits_score, words_score * words_weight, incoming_score * incoming_weight, outgoing_score * outgoing_weight
            
            
def genBuckets(min_incoming = 100, min_outgoing = 100, N=30, M=10, d=5):
    
    outputList = []
    
    generator = utils.getRandomArticle()
    
    while (len(outputList) < N*M):
        
        start = generator.__next__()
        id = utils.traceFromStart(start, d)[-1]
        
        s, s1, s2, s3, s4 = getDifficultyScore(id, min_incoming, min_outgoing)
        if s > -1:
            item = {"article": utils.convertToArticleName(id), 
                    "score": s,
                    "digits": s1,
                    "words":s2,
                    "incoming": s3,
                    "outgoing": s4}
            print(item)
            outputList.append(item)
        
        
    outputList.sort(key = lambda x: x["score"])
    
    #for item in outputList:#[1:int(len(outputList)/2)]: 
    #    print(item)
    
    return outputList#[1:int(len(outputList)/2)]



def genPrompts():
    
    output = genBuckets(min_incoming = 100, min_outgoing = 100, N=10, M=10, d=5)
    
    return output