import discord
from discord.ext import commands, tasks

import json
import pymysql
from pymysql.cursors import DictCursor
import datetime
import os

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
    return f"We currently have {prompts_left} consecutive future prompts left."


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
                # print(report_str)
                await channel.send(report_str)
        func.before_loop(bot.wait_until_ready)
        async_tasks.append(func)
    for task in async_tasks:
        task.start()
    print('Bot is ready, tasks starting...')


DEFAULT_DB_NAME='wikipedia_speedruns'
def get_database(db_name=DEFAULT_DB_NAME):
    # Load database settings from
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
