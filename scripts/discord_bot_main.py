import json
import pymysql
import datetime
import os

import discord
from discord.ext import commands, tasks

from pymysql.cursors import DictCursor

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

channel_id = int(os.getenv('CHANNEL_ID'))
bot_token = os.getenv('BOT_TOKEN')

def _get_new_user_count(conn):
    query = """
    SELECT COUNT(*) AS count FROM users WHERE join_date >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """
    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        count = cursor.fetchone()['count']
        conn.commit()
        return count

def _get_new_run_count(conn):
    query = """
    SELECT COUNT(*) AS count FROM sprint_runs WHERE start_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """
    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        count = cursor.fetchone()['count']
        conn.commit()
        return count
    
def _count_consecutive_future_prompts(conn):
    query = """
    SELECT active_start FROM sprint_prompts WHERE active_start > DATE(NOW()) ORDER BY active_start
    """
    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        dates = [row['active_start'].date() for row in cursor.fetchall()]  # Convert datetime to date
        conn.commit()
    
    if not dates:
        return 0

    count = 0
    current_date = datetime.date.today() + datetime.timedelta(days=1)
    for date in dates:
        if date != current_date:
            break
        count += 1
        current_date += datetime.timedelta(days=1)
    return count

def daily_summary_stats(conn):
    new_user_count = _get_new_user_count(conn)
    new_run_count = _get_new_run_count(conn)
    return f"""New users in the last 24 hours: {new_user_count}
New runs in the last 24 hours: {new_run_count}"""
    
def potd_status_check(conn):
    prompts_left = _count_consecutive_future_prompts(conn)
    output = f"We currently have {prompts_left} consecutive future prompts left."
    if prompts_left < 7:
        output += "\nWARNING - add more prompts!"
    return output

def _get_num_cmty_submissions(conn, daily=False, sprints=True):
    query = f"""
    SELECT COUNT(*) AS count FROM cmty_pending_prompts_{'sprints' if sprints else 'marathon'}
    """
    if daily:
        query += " WHERE submitted_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
    with conn.cursor(cursor=DictCursor) as cursor:
        cursor.execute(query)
        count = cursor.fetchone()['count']
        conn.commit()
        return count

def cmty_submission_stats(conn):
    sprint_total = _get_num_cmty_submissions(conn)
    marathon_total = _get_num_cmty_submissions(conn, sprints=False)
    sprint_daily = _get_num_cmty_submissions(conn, daily=True)
    marathon_daily = _get_num_cmty_submissions(conn, daily=True, sprints=False)
    return f"""Cmty sprints submitted in the last 24 hours: {sprint_daily}
Cmty marathons submitted in the last 24 hours: {marathon_daily}
Total pending cmty sprints: {sprint_total}
Total pending cmty marathons: {marathon_total}"""    


bot_reports = [
    {
        'name': 'daily_summary_stats',
        'target_channel': channel_id,
        'interval': {'hours': 24},
        'func': daily_summary_stats
    },
    {
        'name': 'potd_status_check',
        'target_channel': channel_id,
        'interval': {'hours': 24},
        'func': potd_status_check
    },
    {
        'name': 'daily_cmty_submission_stats',
        'target_channel': channel_id,
        'interval': {'hours': 24},
        'func': cmty_submission_stats
    },
]

async_tasks = []

@bot.event
async def on_ready():
    conn = get_database()
    for report in bot_reports:
        @tasks.loop(**report['interval'])
        async def func(report=report):
            channel = bot.get_channel(report['target_channel'])
            if channel:
                report_str = f"\n{report['name']}\n-------------------\n{report['func'](conn)}"
                await channel.send(report_str)
        func.before_loop(bot.wait_until_ready)
        async_tasks.append(func)
    for task in async_tasks:
        task.start()
    print('Bot is ready, tasks starting...')


DEFAULT_DB_NAME='wikipedia_speedruns'
def get_database(db_name=DEFAULT_DB_NAME):
    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass
    return pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=db_name
    )

if __name__ == '__main__':
    bot.run(bot_token)
