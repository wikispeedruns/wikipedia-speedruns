import pymysql
import argparse
import json

DEFAULT_DB_NAME='wikipedia_speedruns'

def remove_achievement_from_database(cursor, achievement_id):
    cursor.execute("DELETE FROM achievements_progress WHERE achievement_id = (%s)", achievement_id)
    cursor.execute("DELETE FROM achievements WHERE achievement_id = (%s)", achievement_id)
    cursor.execute("DELETE FROM list_of_achievements WHERE achievement_id = (%s)", achievement_id)

def get_achievement_id(cursor, name):
    rows = cursor.execute("SELECT * FROM list_of_achievements WHERE name = (%s)", (name, ))
    if rows == 0:
        return -1
    return cursor.fetchone()["achievement_id"]

def remove_achievement(db_name, name):
    config = json.load(open("../config/default.json"))
    try:
        config.update(json.load(open("../config/prod.json")))
    except FileNotFoundError:
        pass

    conn = pymysql.connect(
        user=config["MYSQL_USER"],
        host=config["MYSQL_HOST"],
        password=config["MYSQL_PASSWORD"],
        database=db_name
    )

    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        
        achievement_id = get_achievement_id(cursor, name)
        if achievement_id == -1:
            raise Exception("achievement is not found in the database; check that the achievement name completely matches")

        message = ""

        while True:
            val = input(f"Are you sure you want to remove this achievement: {name} (yes/no): ")
            if val.lower() == "yes":
                remove_achievement_from_database(cursor, achievement_id)
                message = f"Removed achievement {name} from database"
                break
            elif val.lower() == "no":
                message = "No changes were made"
                break
            else:
                print("This is not a valid input for (yes/no), try again")

        print(message)
        
        conn.commit()
        conn.close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Remove Specified Achievement")
    parser.add_argument('--db_name', type = str, default = DEFAULT_DB_NAME)
    parser.add_argument('achievement_name', type = str)

    args = parser.parse_args()
    remove_achievement(args.db_name, args.achievement_name)