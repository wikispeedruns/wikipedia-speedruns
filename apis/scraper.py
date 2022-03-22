from flask import session, request, abort, Blueprint, jsonify, current_app

from wikispeedruns.scraper import findPaths
from wikispeedruns.scraper_graph_utils import convertToArticleName
from wikispeedruns.prompt_generator import generatePrompts

import json

from tasks import celery

scraper_api = Blueprint("scraper", __name__, url_prefix="/api/scraper")

SCRAPER_TIMEOUT = 20

@scraper_api.post('/path')
def get_path():

    start = request.json['start']
    end = request.json['end']

    result = shortest_path.delay(start, end)
    print(result.wait())

    return "TEST"


@scraper_api.post('/gen_prompts')
def get_prompts():

    n = int(request.json['N'])
    d = 25
    thresholdStart = 200

    # try:
    paths = generatePrompts(thresholdStart=thresholdStart, thresholdEnd=thresholdStart, n=n, dist=d)
    # except Exception as err:
    #     print(err)
    #     return str(err), 500

    outputArr = []

    for path in paths:

        outputArr.append([str(convertToArticleName(path[0])), str(convertToArticleName(path[-1]))])

    return jsonify({'Prompts':outputArr})


@celery.task()
def shortest_path(start: str, end: str):
    return findPaths(start, end)