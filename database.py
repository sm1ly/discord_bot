#!/usr/bin/python3

import sqlite3
from config import DATABASE

# Create base if not exist
def create_tables_if_not_exist():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_data
                (uid INTEGER PRIMARY KEY,
                 coins INTEGER,
                 static_id INTEGER,
                 guest BOOL,
                 moderate BOOL,
                 vip BOOL)''')
    conn.commit()
    conn.close()

# # Load user data from database
def get_user_data(uid):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM user_data WHERE uid=?", (uid,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return False
    else:
        uid, coins, static_id, guest, moderate, vip = row
        return {"coins": coins, "static_id": static_id, "guest": guest, "moderate": moderate, "vip": vip}


# Save user data to database
def save_user_data(user_data):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for uid, data in user_data.items():
        coins = data["coins"]
        static_id = data["static_id"]
        guest = data.get("guest")
        moderate = data.get("moderate")
        vip = data.get("vip")
        c.execute('INSERT OR REPLACE INTO user_data (uid, coins, static_id, guest, moderate, vip) VALUES (?, ?, ?, ?, ?, ?)',
                  (uid, coins, static_id, guest, moderate, vip))
    conn.commit()
    conn.close()


