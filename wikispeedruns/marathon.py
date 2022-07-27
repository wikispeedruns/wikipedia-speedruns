import wikispeedruns.scraper.util as util
import wikispeedruns.scraper.paths as scraper
import math
import random

def getDifficultyScore(id, min_incoming, min_outgoing):

    linkCheckBool, num_incoming, num_outgoing = util.articleLinkNumCheck(id, min_incoming, min_outgoing)
    if not linkCheckBool:
        return -1, 0, 0, 0, 0

    title = util.convertToArticleName(id)
    num_digits = util.countDigitsInTitle(title)
    num_words = util.countWords(title)

    incoming_score = 100 / (1 + math.exp(-0.04 * (num_incoming - min_incoming)))
    outgoing_score = 100 / (1 + math.exp(-0.04 * (num_outgoing - min_outgoing)))

    words_score = 0.7 * math.pow(num_words, 3) - 11.41 * math.pow(num_words, 2) + 41.2 * num_words + 48.67
    if num_words == 2:
        words_score * 0.5

    digits_score = 0
    if num_digits == 4 or num_digits == 0:
        digits_score = 100

    digits_weight = 1.5
    words_weight = 5
    incoming_weight = 8.5
    outgoing_weight = 10

    ds = digits_weight * digits_score
    ws = words_score * words_weight
    iS = incoming_score * incoming_weight
    oS = outgoing_score * outgoing_weight

    final = ds + ws + iS + oS

    return final, (ds, num_digits), (ws, num_words), (iS, num_incoming), (oS, num_outgoing)


def genBatch(prevBatch, min_incoming=100, min_outgoing=100, N=10, d=2):

    outputList = []

    generator = util.getRandomArticle()

    while (len(outputList) < N):

        mid = -1
        try:
            rand = generator.__next__()
            if not util.articleLinkNumCheck(rand, int(min_incoming/3), int(min_outgoing/3)):
                continue

            #start = random.choices(prevBucket, k=2)
            start = random.choice(prevBatch)
            if not type(start) is int:
                start = util.convertToID(start['a'])

            p1 = scraper.findPaths(rand, start)['ArticlesIDs']
            #p1 = scraper.findPaths(rand, start[0], id=True)['ArticlesIDs']
            #p2 = scraper.findPaths(rand, start[1], id=True)['ArticlesIDs']
            #p3 = scraper.findPaths(p1[int(len(p1)/2)], p2[int(len(p2)/2)], id=True)['ArticlesIDs']
            mid = p1[int(len(p1)/2)]
        except RuntimeError as e:
            print(e)
            continue

        s = -1
        id = -1
        while (s == -1):
            id = util.traceFromStart(mid, d)[-1]
            s, s1, s2, s3, s4 = getDifficultyScore(id, min_incoming, min_outgoing)
            print("Checked: " + util.convertToArticleName(id) + " " + str(s))


        item = {"a": util.convertToArticleName(id),
                "s": round(s, 1)}#,
                #"digits": s1,
                #"words":s2,
                #"incoming": s3,
                #"outgoing": s4}

        outputList.append(item)


    outputList.sort(key = lambda x: x["s"])

    for item in outputList:#[1:int(len(outputList)/2)]:
        print(item)

    return outputList#[1:int(len(outputList)/2)]


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def genPrompts(initBatch, batches=5, nPerBatch=10, buckets=5):

    mi = 95
    mo = 95

    batchesArr = []

    batchesArr.append(genBatch(util.convertNamePathToID(initBatch), min_incoming = mi, min_outgoing = mo, N=nPerBatch))

    for i in range(batches-1):
        batchesArr.append(genBatch(batchesArr[i], min_incoming = mi-(i+1)*1/(2*batches), min_outgoing = mo-(i+1)*1/(2*batches), N=nPerBatch))

    batchesArr = [j for i in batchesArr for j in i]

    batchesArr.sort(key = lambda x: -x["s"])

    final = list(split(batchesArr, buckets))

    return [[x['a'] for x in b] for b in final]

    """
    {"start": "Dragonfly", "seed": "123456", "initcheckpoints": ["Insect wing", "Bicycle", "Environmentalism", "DNA", "Kentucky Senate"], "checkpoints": [["John McCain", "Donald Trump", "Soviet Union", "South Korea", "Czech Republic", "Javanese language", "Jim Cummings", "Achaemenid Empire", "Marco Rubio", "Hasmonean dynasty"], ["Vichy France", "Bruce Springsteen", "South Asia", "Chicago Loop", "Solomon Islands", "Han dynasty", "Eastern Europe", "Sumerian language", "Art movement", "Forensic science"], ["Thelonious Monk", "Cell membrane", "Volcanic ash", "WBAL-TV", "Maren Morris", "Ancient Greek", "Persian carpet", "Joey Jordison", "New York City", "Warner Music Group"], ["Washington County, Alabama", "Birdman (rapper)", "Climate change adaptation", "Bart D. Ehrman", "Philadelphia", "Italy", "Methodism", "WWE", "Bahrain", "Wisconsin"], ["Beijing", "Ukraine", "Russia", "Nanjing", "England", "Volga", "Canal", "Stoicism", "Euronext", "William Chambers (architect)"], ["Judo", "Ukrainian Greek Catholic Church", "Minneapolis\u2013Saint Paul International Airport", "Jonathan Coulton", "Vale of White Horse", "Uffie", "Egg Harbor Township, New Jersey", "United States Department of Energy", "Existence", "Paris Peace Conference (1919\u20131920)"], ["Annonay", "NS\u00cd Runav\u00edk", "10th edition of Systema Naturae", "Secret police", "James Franciscus", "Human Development Index", "Historical linguistics", "Calendar of saints", "Ectoderm", "The New York Times Magazine"]]}
    """