import asyncio
import json
from flask import Blueprint, jsonify
from db import get_db
from pymysql.cursors import DictCursor

from wikispeedruns import stats
from util.decorators import check_admin

stats_api = Blueprint("stats", __name__, url_prefix="/api/stats")

@stats_api.get("/calculate")
@check_admin
def calculate_stats():
    asyncio.create_task(stats.async_calculate_stats())
    return 'Success', 200

@stats_api.get("/all")
@check_admin
def get_total_stats():
    most_recent_stats_query = 'SELECT * FROM `computed_stats` LIMIT 1'

    db = get_db()
    with db.cursor(cursor=DictCursor) as cursor:
        cursor.execute(most_recent_stats_query)
        return jsonify(cursor.fetchall()[0])
