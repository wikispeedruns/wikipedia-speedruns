from wikispeedruns import stats
from flask import Blueprint 

from util.decorators import check_admin

stats_api = Blueprint("stats", __name__, url_prefix="/api/stats")

@stats_api.get("/calculate")
@check_admin
def async_calculate_stats():
    # start a thread, process queries
    return 200

@stats_api.get("/totals")
@check_admin
def get_total_stats():
    return stats.calculate_total_stats()

@stats_api.get("/daily")
@check_admin
def get_daily_stats():
    return stats.calculate_daily_stats()
