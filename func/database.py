#!/usr/bin/python3

import aiosqlite
from config import DATABASE
from func.logger import logger
import pprint


async def execute(query, *args):
    async with aiosqlite.connect(DATABASE) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, args)
            await conn.commit()


async def fetch(query, *args):
    async with aiosqlite.connect(DATABASE) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchone()


# Create table if not exist
async def create_tables_if_not_exist():
    await execute('''CREATE TABLE IF NOT EXISTS user_data
                (uid INTEGER PRIMARY KEY,
                 coins INTEGER,
                 static_id INTEGER,
                 guest BOOL,
                 moderate BOOL,
                 vip BOOL)''')


# Load user data from database by UID
async def get_user_data(uid):
    row = await fetch("SELECT * FROM user_data WHERE uid=?", uid)
    if row is None:
        return False
    else:
        uid, coins, static_id, guest, moderate, vip = row
        return {"coins": coins, "static_id": static_id, "guest": guest, "moderate": moderate, "vip": vip}


# Load user data from database by static_id
async def get_user_data_by_static_id(static_id):
    row = await fetch("SELECT * FROM user_data WHERE static_id=?", static_id)
    if row is None:
        return False
    else:
        uid, coins, static_id, guest, moderate, vip = row
        return {"coins": coins, "uid": uid, "guest": guest, "moderate": moderate, "vip": vip}


# Save user data to database
async def save_user_data(user_data):
    for uid, data in user_data.items():
        coins = data["coins"]
        static_id = data["static_id"]
        guest = data.get("guest")
        moderate = data.get("moderate")
        vip = data.get("vip")
        await execute('INSERT OR REPLACE INTO user_data (uid, coins, static_id, guest, moderate, vip) VALUES (?, ?, ?, ?, ?, ?)',
                      uid, coins, static_id, guest, moderate, vip)


# Save user data to database by static ID
async def save_user_data_by_static_id(user_data):
    for static_id, data in user_data.items():
        coins = data["coins"]
        uid = data["uid"]
        guest = data.get("guest")
        moderate = data.get("moderate")
        vip = data.get("vip")
        await execute('INSERT OR REPLACE INTO user_data (uid, coins, static_id, guest, moderate, vip) VALUES (?, ?, ?, ?, ?, ?)',
                      uid, coins, static_id, guest, moderate, vip)


# Drop table user data
async def drop_table():
    await execute("DROP TABLE IF EXISTS user_data")


# Remove user
async def remove_user(uid):
    await execute("DELETE FROM user_data WHERE uid=?", uid)


# Set moderate flag to true for user with given UID
async def set_user_moderate(uid):
    await execute("UPDATE user_data SET moderate=? WHERE uid=?", True, uid)


async def is_user_moderated(uid):
    row = await fetch("SELECT moderate FROM user_data WHERE uid=?", uid)
    if row is None:
        return False
    return bool(row[0])


# Set moderate flag to true for user with given UID
async def set_user_vip(uid):
    await execute("UPDATE user_data SET vip=? WHERE uid=?", True, uid)


async def is_user_vip(uid):
    row = await fetch("SELECT vip FROM user_data WHERE uid=?", uid)
    if row is None:
        return False
    return bool(row[0])


# disable vip (# for testing purposes)
# async def disable_vip(uid):
#     await execute("UPDATE user_data SET vip=? WHERE uid=?", False, uid)

# ------------------------------------------------------------------------------------
#
#   old code
#
# ------------------------------------------------------------------------------------
#
# import aiosqlite
# from config import DATABASE
# from func.logger import logger
# import pprint
#
#
# # Create table if not exist
# async def create_tables_if_not_exist():
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         await c.execute('''CREATE TABLE IF NOT EXISTS user_data
#                 (uid INTEGER PRIMARY KEY,
#                  coins INTEGER,
#                  static_id INTEGER,
#                  guest BOOL,
#                  moderate BOOL,
#                  vip BOOL)''')
#         await conn.commit()
#
#
# # Load user data from database by UID
# async def get_user_data(uid):
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         await c.execute("SELECT * FROM user_data WHERE uid=?", (uid,))
#         row = await c.fetchone()
#         if row is None:
#             return False
#         else:
#             uid, coins, static_id, guest, moderate, vip = row
#             return {"coins": coins, "static_id": static_id, "guest": guest, "moderate": moderate, "vip": vip}
#
#
# # Load user data from database by static_id
# async def get_user_data_by_static_id(static_id):
#         async with aiosqlite.connect(DATABASE) as conn:
#             c = await conn.cursor()
#             await c.execute("SELECT * FROM user_data WHERE static_id=?", (static_id,))
#             row = await c.fetchone()
#             if row is None:
#                 return False
#             else:
#                 uid, coins, static_id, guest, moderate, vip = row
#                 return {"coins": coins, "uid": uid, "guest": guest, "moderate": moderate, "vip": vip}
#
#
# # Save user data to database
# async def save_user_data(user_data):
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         for uid, data in user_data.items():
#             coins = data["coins"]
#             static_id = data["static_id"]
#             guest = data.get("guest")
#             moderate = data.get("moderate")
#             vip = data.get("vip")
#             await c.execute('INSERT OR REPLACE INTO user_data (uid, coins, static_id, guest, moderate, vip) VALUES (?, ?, ?, ?, ?, ?)',
#                       (uid, coins, static_id, guest, moderate, vip))
#         await conn.commit()
#
#
# # Save user data to database by static ID
# async def save_user_data_by_static_id(user_data):
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         for static_id, data in user_data.items():
#             coins = data["coins"]
#             uid = data["uid"]
#             guest = data.get("guest")
#             moderate = data.get("moderate")
#             vip = data.get("vip")
#             await c.execute('INSERT OR REPLACE INTO user_data (uid, coins, static_id, guest, moderate, vip) VALUES (?, ?, ?, ?, ?, ?)',
#                       (uid, coins, static_id, guest, moderate, vip))
#         await conn.commit()
#
#
# # Drop table user data
# async def drop_table():
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         await c.execute("DROP TABLE IF EXISTS user_data")
#         await conn.commit()
#
#
# # Remove user
# async def remove_user(uid):
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         await c.execute("DELETE FROM user_data WHERE uid=?", (uid,))
#         await conn.commit()
#
#
# # Moderate YES
# async def set_user_moderate(uid):
#     async with aiosqlite.connect(DATABASE) as conn:
#         c = await conn.cursor()
#         await c.execute("UPDATE user_data SET moderate=? WHERE uid=?", (True, uid))
#         await conn.commit()
