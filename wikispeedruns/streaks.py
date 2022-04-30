from db import get_db
from pymysql.cursors import DictCursor
import json

def get_current_streak(user_id):

    query = """
    SELECT
        DATEDIFF(CURDATE(), run_date) AS d
    FROM (
        SELECT
            CAST(start_time AS DATE) as run_date
        FROM sprint_runs
        INNER JOIN sprint_prompts ON sprint_prompts.prompt_id = sprint_runs.prompt_id
        WHERE
            user_id=%s
            AND sprint_runs.start_time BETWEEN sprint_prompts.active_start AND sprint_prompts.active_end
            AND rated
            AND end_time IS NOT NULL
        GROUP BY run_date
        ORDER BY run_date DESC )
    as date_diff
    """
    with get_db().cursor(cursor=DictCursor) as cursor:
        cursor.execute(query, (user_id,))
        dates = cursor.fetchall()

    dates = [x['d'] for x in dates]
        
    if len(dates) == 0:
        today = 0
        streak = 0
    else:
        if dates[0] == 0: today = 1
        else: today = 0
        
        
        if dates[0] == 0 or dates[0] == 1:
            streak = 0
            for i in range(len(dates)):
                if dates[i] > i + dates[0]:
                    break
                streak += 1
        else: streak = 0        
        
    res = {'done_today': today, 'streak': streak}
    
    return res
