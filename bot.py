#!/usr/bin/python3

import discord
import asyncio
import config
from datetime import datetime
import random
from logger import logger
from database import create_tables_if_not_exist, get_user_data, save_user_data

client = discord.Client(intents=discord.Intents.all(), dm_intents=discord.Intents.all(), log_handler=None)

# Initialize table and load user data from database
create_tables_if_not_exist()

def random_hex_color():
    """Возвращает случайный цвет в формате hex"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return "0x{:02x}{:02x}{:02x}".format(r, g, b)

async def menu(message):
    buttons = [
        discord.ui.Button(label="Организация транспортировки | 2 Монеты", custom_id="button_1",style=discord.ButtonStyle.blurple),
        discord.ui.Button(label="Услуги консьержа 24/7 | 1 монета", custom_id="button_2",style=discord.ButtonStyle.blurple),
        discord.ui.Button(label="Юридическая помощь | 1 монета", custom_id="button_3",style=discord.ButtonStyle.green),
        discord.ui.Button(label="Услуги аренды спортивного инвентаря | Индивидуально", custom_id="button_4",style=discord.ButtonStyle.blurple, disabled=True),
        discord.ui.Button(label="Сервис удаления персональных данных | 10 монет", custom_id="button_5",style=discord.ButtonStyle.green, disabled=True),
        discord.ui.Button(label="Эксклюзивные вечеринки | 10 монет", custom_id="button_6",style=discord.ButtonStyle.red, disabled=True),
        discord.ui.Button(label="Специальные мероприятия | 10 монет", custom_id="button_7",style=discord.ButtonStyle.red, disabled=True)
    ]
    buttons_vip = [
        discord.ui.Button(label="Организация транспортировки | 2 Монеты", custom_id="button_1",style=discord.ButtonStyle.blurple),
        discord.ui.Button(label="Услуги консьержа 24/7 | 1 монета", custom_id="button_2",style=discord.ButtonStyle.blurple),
        discord.ui.Button(label="Юридическая помощь | 1 монета", custom_id="button_3",style=discord.ButtonStyle.green),
        discord.ui.Button(label="Услуги аренды спортивного инвентаря | Индивидуально", custom_id="button_4",style=discord.ButtonStyle.blurple),
        discord.ui.Button(label="Сервис удаления персональных данных | 10 монет", custom_id="button_5",style=discord.ButtonStyle.green),
        discord.ui.Button(label="Эксклюзивные вечеринки | 10 монет", custom_id="button_6",style=discord.ButtonStyle.red),
        discord.ui.Button(label="Специальные мероприятия | 10 монет", custom_id="button_7",style=discord.ButtonStyle.red)
    ]
    view = discord.ui.View()
    for button in buttons:
        view.add_item(button)

    # отправляем сообщение пользователю
    msg = await message.author.send("Выберите услугу, которую хотите приобрести:", view=view)

    # удаляем исходное сообщение
    if isinstance(message.channel, discord.TextChannel):
        await message.delete()

    # ждем выбора пользователя или таймаута
    try:
        interaction = await client.wait_for("button_click", timeout=30.0, check=lambda i: i.message.id == msg.id and i.user.id == message.author.id)
    except asyncio.TimeoutError:
        await msg.edit(content="Время выбора истекло.", view=None)
    else:
        on_interaction(interaction)

async def threader(local_name, roles, interaction, price, uid):
    user_data[uid]["coins"] -= price
    save_user_data(user_data)
    channel = client.get_channel(config.CHANNEL_ID_PAID_SERVICE)  # получаем объект канала по ID
    thread = await channel.create_thread(name=f"{local_name} | Guest", reason="Новый заказ", invitable=False)
    user_mention = interaction.user.mention
    await thread.send(f"{user_mention}, Поздравляем, Вы купили: {local_name}.\nВ чат добавлены:")
    for role in roles:
        await thread.send(role.mention)
    balance = user_data[uid]["coins"]
    await thread.send(f"У Вас осталось {balance} монет.")

@client.event
async def on_ready():
    logger.info('Logged in as {0.user}'.format(client))
    global guild
    guild = client.get_guild(config.GUILD_ID)
    # for role in guild.roles:
    #     logger.info(f"{role.name} - {role.id}")  # выводим имя и ID каждой роли
    global bot_administrators
    logger.info("Bot administrators:")
    bot_administrators = []
    for role in guild.roles:
        if role.id == config.ROLE_ID_TheRoyalFamily or role.id == config.ROLE_ID_TheHeadInnkeeper:
            for member in role.members:
                bot_administrators.append(member.id)
                user = await client.fetch_user(member.id)
                logger.info(f"{member.id} | {user}")
    logger.info("Bot started!")

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
        elif get_user_data(uid):
            await message.channel.set_permissions(message.author, send_messages=False)
            await message.delete()
            await message.author.send(f"{author}, вы уже получили свою монету!")
            server = message.author.guild
            role = discord.utils.get(server.roles, id=1083494042035298456)
            if role is not None:
                await message.author.add_roles(role)
        else:

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
        if uid in user_data and user_data[uid]["coins"] >= 10:
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
        if uid not in bot_administrators:
            await message.author.send("У Вас нет прав для использования команды !add_coins.")
            if isinstance(message.channel, discord.TextChannel):
                await message.delete()
            return

        try:
            args = message.content.split()
            static_id = int(args[1])
            amount = int(args[2])
        except:
            await message.author.send("Invalid arguments. Usage: !add_coins <static_id> <amount>")
            if isinstance(message.channel, discord.TextChannel):
                await message.delete()
            return

        for uid, data in user_data.items():
            if data["static_id"] == static_id:
                data["coins"] += amount
                save_user_data(user_data)
                await message.author.send(f"Успешно добавлено {amount} монет статику {static_id}!")
                if isinstance(message.channel, discord.TextChannel):
                    await message.delete()
                # Получаем текущую дату и время
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Создаем embed сообщение
                random_color = random_hex_color()
                print(random_color)
                embed = discord.Embed(title='current_time', color=random_color)
                embed.add_field(name='Команда', value=command, inline=False)
                embed.add_field(name='Пользователь', value=message.author.id, inline=False)
                embed.add_field(name='Дата и время', value=current_time, inline=False)

                # Получаем дополнительный канал для записи истории
                history_add_coins_channel = client.get_channel(config.CHANNEL_ID_HISTORY_ADD_COINS)

                # Отправляем embed сообщение в дополнительный канал
                await history_add_coins_channel.send(embed=embed)
                return

        await message.author.send(f"Статик {static_id} не найден в базе данных.")

    if message.content.startswith('!check_balance'):
        if not get_user_data(uid):
            await message.author.send(f"{author}, у Вас нет баланса, видимо Вы не оплатили ни одной монеты.")
        else:
            balance = get_user_data[uid]["coins"]
            await message.author.send(f"{author}, Ваш баланс: {balance} монет.")

        if isinstance(message.channel, discord.TextChannel):
            await message.delete()

    if isinstance(message.channel, discord.TextChannel) and message.content.startswith('!purge'):
        if uid not in bot_administrators:
            await message.author.send("У Вас нет прав для использования команды !purge.")
            await message.delete()
            return
        try:
            await message.channel.purge(limit=50)
            await message.channel.send("Successfully deleted the last 50 messages.", delete_after=5.0)
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")
        finally:
            await message.delete()

    if isinstance(message.channel, discord.DMChannel) and config.REACTION_SYMBOL in message.content:
        await message.author.send(f"{message.author.display_name}, невозможно получить монету в dm. Пройдите в <#{config.CHANNEL_ID_I_PAID}> и поставьте `+`")

    if message.content.startswith('!menu'):
        if uid not in user_data:
            await message.author.send(f"Кажется Вы еще не являетесь нашим Гостем или VIP-Гостем! Для того чтобы стать нашим гостем и получить доступ к услугам, необходимо приобрести хотя бы одну монету. Для VIP-гостей, которым доступен расширенный спектр услуг, необходимо внести единоразовый взнос в виде 10 монет. Подробнее в <#{config.CHANNEL_ID_HOW_WE_WORK}>")
            await message.delete()
        else:
            await menu(message)

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
        await threader(local_name, roles, interaction, price, uid)
    else:
        await interaction.user.send("У вас недостаточно монет для покупки этой позиции!")


client.run(config.token)
