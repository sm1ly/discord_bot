#!/usr/bin/python3

import discord
import asyncio
import config
from datetime import datetime
from database import get_user_data, get_user_data_by_static_id, save_user_data, save_user_data_by_static_id
import func
from func import client
from logger import logger

@client.event
async def on_ready():
    await func.ready()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    logger.info('{0.author.display_name} [{0.author}]: {0.content}'.format(message))

    uid = message.author.id
    author = message.author.display_name

    if isinstance(message.channel, discord.TextChannel) and message.channel.id == config.CHANNEL_ID_I_PAID and message.content.startswith(config.REACTION_SYMBOL):
        static_id = author.split("|")[1].strip() if "|" in author else None
        if static_id is None:
            await message.delete()
            await message.author.send("Для того чтобы получить монету, необходимо указать static_id в никнейме пользователя. Например: Ahu Enen | 123456")
        elif await get_user_data(uid) and await get_user_data_by_static_id(static_id):
            await message.channel.set_permissions(message.author, send_messages=False)
            await message.delete()
            await message.author.send(f"{author}, вы уже получили свою монету!")
            server = message.author.guild
            role = discord.utils.get(server.roles, id=1083494042035298456)
            if role is not None:
                await message.author.add_roles(role)
        else:

            user_data = {}
            user_data[uid] = {"coins": 1, "static_id": static_id, "guest": True, "moderate": True, "vip": False}
            save_user_data(user_data)

            # Добавляем роль "Guest" пользователю
            server = message.author.guild
            role = discord.utils.get(server.roles, id=1083494042035298456)
            if role is not None:
                await message.author.add_roles(role)

            await message.channel.set_permissions(message.author, send_messages=False)
            await message.delete()
            await message.author.send(f"{author}, вы получили свою монету! И стали нашим Гостем. Теперь для Вас доступен новый функционал!")
            await message.author.send(f"Подробнее в <#{config.CHANNEL_ID_SERVICE_COST}>")

    if isinstance(message.channel, discord.TextChannel) and message.channel.id == config.CHANNEL_ID_I_PAID_VIP and message.content.startswith(config.REACTION_SYMBOL):
        # static_id = author.split("|")[1].strip() if "|" in author else None
        if await get_user_data(uid) and await get_user_data(uid)["coins"] >= 10:
            # Добавляем роль "VIP Guest" пользователю
            server = message.author.guild
            role = discord.utils.get(server.roles, id=1083494100151574558)
            if role is not None:
                await message.author.add_roles(role)
            await message.channel.set_permissions(message.author, send_messages=False)
            await message.delete()
            await message.author.send(f"{author}, Вы потратили 10 монет! Вы стали VIP! Теперь для Вас доступен новый функционал!")
            await message.author.send(f"Подробнее в <#{config.CHANNEL_ID_VIP_SERVICE_COST}>")
        else:
            await message.delete()
            await message.author.send(f"{author}, Кажется Вы не внесли взнос в размере 10 монет!")

    if message.content.startswith('!add_coins'):
        await func.add_coins(uid, message)

    if message.content.startswith('!check_balance'):
        await func.check_balance(uid, author, message)

    if isinstance(message.channel, discord.TextChannel) and message.content.startswith('!purge'):
        await func.purge(uid, message)

    if isinstance(message.channel, discord.DMChannel) and config.REACTION_SYMBOL in message.content:
        await message.author.send(f"{message.author.display_name}, невозможно получить монету в dm. Пройдите в <#{config.CHANNEL_ID_I_PAID}> и поставьте `+`")

    if message.content.startswith('!menu'):
        if uid not in user_data:
            await message.author.send(f"Кажется Вы еще не являетесь нашим Гостем или VIP-Гостем! Для того чтобы стать нашим гостем и получить доступ к услугам, необходимо приобрести хотя бы одну монету. Для VIP-гостей, которым доступен расширенный спектр услуг, необходимо внести единоразовый взнос в виде 10 монет. Подробнее в <#{config.CHANNEL_ID_HOW_WE_WORK}>")
            await message.delete()
        else:
            await func.menu(message)

@client.event
async def on_interaction(interaction):
    uid = interaction.user.id
    custom_id = interaction.data["custom_id"]
    roles = []
    local_name = ""
    price = 0

    if custom_id == "button_1":
        await interaction.response.send_message("Вы выбрали организацию транспортировки.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Courier),
            guild.get_role(config.ROLE_ID_Porter),
            guild.get_role(config.ROLE_ID_Security),
            guild.get_role(config.ROLE_ID_Technician)
        ]
        local_name = "Организация Транспортировки" # | Guest Static"
        price = 2
    elif custom_id == "button_2":
        await interaction.response.send_message("Вы выбрали услуги консьержа 24/7.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Concierge),
            guild.get_role(config.ROLE_ID_Porter)
        ]
        local_name = "Услуги Консьержа 24/7 | Guest Static"
        price = 1
    elif custom_id == "button_3":
        await interaction.response.send_message("Вы выбрали юридическую помощь.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Briber)
        ]
        local_name = "Юридическая Помощь | Guest Static"
        price = 1
    elif custom_id == "button_4":
        await interaction.response.send_message("Вы выбрали услуги аренды спортивного инвентаря.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Merchant)
        ]
        local_name = "Аренда Спортивного Инвентаря | Guest Static"
        price = 0
    elif custom_id == "button_5":
        await interaction.response.send_message("Вы выбрали сервис удаления персональных данных.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Hacker)
        ]
        local_name = "Удавление Персональных Данных | Guest Static"
        price = 10
    elif custom_id == "button_6":
        await interaction.response.send_message("Вы выбрали эксклюзивные вечеринки.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Blackmailer)
        ]
        local_name = "Эксклюзивные Вечеринки | Guest Static"
        price = 10
    elif custom_id == "button_7":
        await interaction.response.send_message("Вы выбрали специальные мероприятия.", ephemeral=True)
        roles = [
            guild.get_role(config.ROLE_ID_TheHeadInnkeeper),
            guild.get_role(config.ROLE_ID_TheRoyalFamily),
            guild.get_role(config.ROLE_ID_Don)
        ]
        local_name = "Специальное Мероприятие | Guest Static"
        price = 10
    if uid not in user_data:
        await interaction.user.send(f"У вас нет монет. Оплатите и пройдите в <#{config.CHANNEL_ID_I_PAID}> и поставьте `+`")
        return
    if user_data[uid]["coins"] >= price:
        await func.threader(local_name, roles, interaction, price, uid)
    else:
        await interaction.user.send("У вас недостаточно монет для покупки этой позиции!")


client.run(config.token)
