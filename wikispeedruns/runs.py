from flask import jsonify, request, Blueprint, session
from datetime import datetime
import json
from typing import List, Literal, Tuple, TypedDict, Optional

from db import get_db, get_db_version
from pymysql.cursors import DictCursor

class PathEntry(TypedDict):
    article: str 
    timeReached: float 
    loadTime: float

def update_sprint_run(run_id: int, start_time: datetime, end_time: datetime, 
                      path: List[PathEntry], finished: bool):
                      
    pathStr = json.dumps({
        'version': get_db_version(),
        'path': path
    })

    duration = (end_time - start_time).total_seconds()
    total_load_time = sum([entry.get('loadTime') for entry in path])
    play_time = duration - total_load_time

    query_args = {
        "run_id": run_id,
        "start_time": start_time,
        "end_time": end_time,
        "play_time": play_time,
        "finished": finished,
        "path": pathStr
    }
    
    db = get_db()
    with db.cursor() as cursor:
        query = f'''
        UPDATE `sprint_runs` 
        SET `start_time`=%(start_time)s, `end_time`=%(end_time)s, `play_time`=%(play_time)s, `finished`=%(finished)s, `path`=%(path)s
        WHERE `run_id`=%(run_id)s
        '''

        cursor.execute(query, query_args)
        db.commit()

    return run_id
