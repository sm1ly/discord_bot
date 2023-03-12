#!/usr/bin/python3

import disnake
import asyncio
import config
from database import get_user_data, get_user_data_by_static_id, save_user_data, save_user_data_by_static_id
import func
from func import client
from logger import logger
from interactions import interactions

@client.event
async def on_ready():
    await func.ready()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    logger.info('{0.author.display_name} [{0.author}]: {0.content}'.format(message))

    uid = message.author.id
    author = message.author

    if isinstance(message.channel, disnake.TextChannel) and message.channel.id == config.CHANNEL_ID_I_PAID and message.content.startswith(config.REACTION_SYMBOL):
        await func.paid_check(uid, author, message)

    if isinstance(message.channel, disnake.TextChannel) and message.channel.id == config.CHANNEL_ID_I_PAID_VIP and message.content.startswith(config.REACTION_SYMBOL):
        await func.paid_vip_check(uid, author, message)

    if message.content.startswith('!add_coins'):
        await func.add_coins(uid, message)

    if message.content.startswith('!check_balance'):
        logger.info("bot.py !check_balance")
        await func.check_balance(uid, author, message)

    if isinstance(message.channel, disnake.TextChannel) and message.content.startswith('!purge'):
        await func.purge(uid, message)

    if isinstance(message.channel, disnake.DMChannel) and config.REACTION_SYMBOL in message.content:
        await message.author.send(f"{message.author.display_name}, невозможно получить монету в dm. Пройдите в <#{config.CHANNEL_ID_I_PAID}> и поставьте `+`")

    if message.content.startswith('!menu'):
        await func.menu(uid, message)

# @client.event
# async def on_interaction(interaction):
#     await interactions(interaction)


client.run(config.token)
