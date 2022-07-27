from tabnanny import check
from flask import session, request, abort, Blueprint, jsonify, current_app
from util.async_result import register_async_endpoint

from wikispeedruns.scraper.paths import findPaths
from wikispeedruns.scraper.util import convertToID

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
    start_id = convertToID(start)
    end_id = convertToID(end)

    return findPaths(start_id, end_id)

register_async_endpoint(scraper_api, "/path", shortest_path, shortest_path_parse)


# Test

def test_parse(task, request):
    return task.delay()

@celery.task(time_limit=1)
def test():
    while(True):
        pass

register_async_endpoint(scraper_api, "/test", test, test_parse)
