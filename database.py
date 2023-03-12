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
                 static_id TEXT,
                 guest BOOL,
                 moderate BOOL,
                 vip BOOL)''')
    conn.commit()
    conn.close()

# Load user data from database
def load_user_data():
    user_data = {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for row in c.execute('SELECT * FROM user_data'):
        user_data[row[0]] = {"coins": row[1], "static_id": row[2]}
    conn.close()
    return user_data

# Save user data to database
def save_user_data(user_data):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for uid, data in user_data.items():
        coins = data["coins"]
        static_id = data["static_id"]
        c.execute('REPLACE INTO user_data (uid, coins, static_id) VALUES (?, ?, ?)', (uid, coins, static_id))
    conn.commit()
    conn.close()
