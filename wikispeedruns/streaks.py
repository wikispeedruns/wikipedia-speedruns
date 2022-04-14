from db import get_db
from pymysql.cursors import DictCursor

def get_current_streak(user_id):

    query = """
    SELECT IF(MAX(run_date)=CURDATE(), 1, 0) as done_today, COUNT(*) AS streak FROM (
        SELECT
            run_date,
            DATEDIFF(CURDATE(), run_date) AS Diff,
            ROW_NUMBER() OVER(ORDER BY(run_date) DESC) AS rown
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
        as temp)
    as temp2 WHERE Diff <= rown
    """
    with get_db().cursor(cursor=DictCursor) as cursor:
        result = cursor.execute(query, (user_id,))
        return cursor.fetchone()
