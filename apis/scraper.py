from tabnanny import check
from flask import session, request, abort, Blueprint, jsonify, current_app
from util.async_result import register_async_endpoint

from wikispeedruns.scraper import findPaths
from wikispeedruns.scraper_graph_utils import convertToArticleName
from wikispeedruns.prompt_generator import generatePrompts

import json

from util.decorators import check_request_json

from tasks import celery

scraper_api = Blueprint("scraper", __name__, url_prefix="/api/scraper")

SCRAPER_TIMEOUT = 20

# Shortest path

def shortest_path_parse(task, request):
    start = request.json['start']
    end = request.json['end']
    return task.delay(start, end)

@celery.task(time_limit=SCRAPER_TIMEOUT)
def shortest_path(start: str, end: str):
    return findPaths(start, end)

register_async_endpoint(scraper_api, "/path", shortest_path, shortest_path_parse)


# Prompt Generation

def generate_prompt_parse(task, request):
    return task.delay()

@celery.task(time_limit=SCRAPER_TIMEOUT)
def generate_prompt():
    d = 25
    thresholdStart = 200
    paths = generatePrompts(thresholdStart=thresholdStart, thresholdEnd=thresholdStart, n=1, dist=d)

    outputArr = []

    for path in paths:
        outputArr.append([str(convertToArticleName(path[0])), str(convertToArticleName(path[-1]))])

    return {'Prompts': outputArr}


register_async_endpoint(scraper_api, "/gen_prompts", generate_prompt, generate_prompt_parse)

# Test

def test_parse(task, request):
    return task.delay()

@celery.task(time_limit=1)
def test():
    while(True):
        pass

register_async_endpoint(scraper_api, "/test", test, test_parse)
