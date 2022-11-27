from flask import Blueprint, jsonify
from db import get_db
from pymysql.cursors import DictCursor

from wikispeedruns import stats
from util.decorators import check_admin
from util.lock_utils import locked
from util.process_utils import start_process

stats_api = Blueprint("stats", __name__, url_prefix="/api/stats")

def _calc_stats(lock):
    with lock: 
        stats.calculate()

@stats_api.get("/calculate")
@check_admin
def calculate_stats():
    if locked(stats.calc_stat_lock):
        return 'Stat calculation in progress, check back later.', 503

    start_process(_calc_stats, (stats.calc_stat_lock,))
    return 'Success', 200

@stats_api.get("/all")
@check_admin
def get_total_stats():
    most_recent_stats_query = 'SELECT * FROM `computed_stats` ORDER BY `timestamp` DESC LIMIT 1'

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(most_recent_stats_query)
        return jsonify(cursor.fetchall()[0])
