from flask import session, request, abort, Blueprint, jsonify, current_app

from wikispeedruns.scraper import generatePrompts, convertToArticleName


scraper_api = Blueprint("scraper", __name__, url_prefix="/api/scraper")


@scraper_api.post('/path')
def get_path():
    
    start = request.json['start']
    end = request.json['end']
    
    
    try:
        output = timer(scraper_timeout, findPaths, start, end)
    except Exception as err:
        print(f"ERROR {str(err)}")
        return str(err), 500
    
    """
    pool = Pool(processes=1)
    result = pool.apply_async(findPaths, (start, end))
    
    try:
        output = result.get(timeout=scraper_timeout)
    except TimeoutError:
        msg = f"Scraper search exceeded {scraper_timeout} seconds"
        print(msg)
        return msg, 500
    except Exception as err:
        print(f"ERROR {str(err)}")
        return str(err), 500
    """
    
    return jsonify(output)
    

@scraper_api.post('/gen_promptss')
def get_prompts():
    
    n = int(request.json['N']) - 1
    d = 25
    thresholdStart = 200
    
    try:
        paths = generatePrompts(thresholdStart=thresholdStart, thresholdEnd=thresholdStart, n=n, dist=d)
    except Exception as err:
        print(err)
        return str(err), 500
    
    outputArr = []
    
    for path in paths:
        
        outputArr.append([str(convertToArticleName(path[0])), str(convertToArticleName(path[-1]))])
        
    return jsonify({'Prompts':outputArr})
