import json
from flask import Blueprint, jsonify
from db import get_db
from pymysql.cursors import DictCursor

from wikispeedruns import stats
from util.decorators import check_admin

stats_api = Blueprint("stats", __name__, url_prefix="/api/stats")

@stats_api.get("/calculate")
@check_admin
def async_calculate_stats():
    # start a thread, process queries
    stats.calculate_stats()
    return 'succ', 200

@stats_api.get("/all")
@check_admin
def get_total_stats():
    most_recent_stats_query = 'SELECT * FROM `computed_stats` LIMIT 1'

    db = get_db()
    res = None

    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(most_recent_stats_query)
        res = cursor.fetchall()[0]

    stat_json = json.loads(res['stats_json'])
    return jsonify(stat_json['stats'])