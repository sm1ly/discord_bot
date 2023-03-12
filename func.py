#!/usr/bin/python3

import asyncio
import disnake
from database import create_tables_if_not_exist, get_user_data, get_user_data_by_static_id, save_user_data, save_user_data_by_static_id
from logger import logger
import random
import config
from datetime import datetime

client = disnake.Client(intents=disnake.Intents.all())

def generate_random_color():
    # generate a random hex color code
    r = lambda: random.randint(0, 255)
    color = int('0x{:02X}{:02X}{:02X}'.format(r(), r(), r()), 16)
    return color

async def menu(uid, message):
    if uid not in user_data:
        await message.author.send(
            f"Кажется Вы еще не являетесь нашим Гостем или VIP-Гостем! Для того чтобы стать нашим гостем и получить доступ к услугам, необходимо приобрести хотя бы одну монету. Для VIP-гостей, которым доступен расширенный спектр услуг, необходимо внести единоразовый взнос в виде 10 монет. Подробнее в <#{config.CHANNEL_ID_HOW_WE_WORK}>")
        await message.delete()
    else:
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
    await save_user_data(user_data)
    channel = client.get_channel(config.CHANNEL_ID_PAID_SERVICE)  # получаем объект канала по ID
    thread = await channel.create_thread(name=f"{local_name} | Guest", reason="Новый заказ", invitable=False)
    user_mention = interaction.user.mention
    await thread.send(f"{user_mention}, Поздравляем, Вы купили: {local_name}.\nВ чат добавлены:")
    for role in roles:
        await thread.send(role.mention)
    balance = user_data[uid]["coins"]
    await thread.send(f"У Вас осталось {balance} монет.")

async def check_balance(uid, author, message):
    logger.info("func.py !check_balance 1")
    user_data = await get_user_data(uid)
    logger.info("func.py !check_balance 2")
    logger.info(user_data)
    logger.info(f'func.py UID {uid}')
    if not user_data:
        logger.info(f'func.py author {author}')
        await author.send_message(f"{author}, у Вас нет баланса, видимо Вы не оплатили ни одной монеты.")
        logger.info(f'func.py author2 {author}')
        return

    balance = user_data["coins"]
    await author.send(f"{author}, Ваш баланс: {balance} монет.")

    if isinstance(message.channel, disnake.TextChannel):
        await message.delete()

async def add_coins(uid: int, message: disnake.Message):
    if uid not in bot_administrators:
        await message.author.send("У Вас нет прав для использования команды !add_coins.")
        if isinstance(message.channel, disnake.TextChannel):
            await message.delete()
        return

    try:
        args = message.content.split()
        static_id = int(args[1])
        amount = int(args[2])
    except:
        await message.author.send("Invalid arguments. Usage: !add_coins <static_id> <amount>")
        if isinstance(message.channel, disnake.TextChannel):
            await message.delete()
        return

    user_data = await get_user_data_by_static_id(static_id)
    if user_data:
        if amount <= 0:
            await message.author.send("Количество монет не может быть отрицательным!")
            return

        user_data["coins"] += amount
        await save_user_data_by_static_id(user_data)

        await message.author.send(f"Успешно добавлено {amount} монет статику {static_id}!")
        if isinstance(message.channel, disnake.TextChannel):
            await message.delete()

        # Получаем текущую дату и время
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Создаем embed сообщение
        color = generate_random_color()
        embed = disnake.Embed(title='Начисление монет', color=color)
        embed.add_field(name='Кто', value=f'<@{uid}>', inline=False)
        embed.add_field(name='Кому', value=f'<@{user_data["uid"]}>', inline=False)
        embed.add_field(name='Статик', value=f'{static_id}', inline=False)
        embed.add_field(name='Сколько монет', value=amount, inline=False)
        embed.add_field(name='Дата и время', value=current_time, inline=False)

        # Получаем дополнительный канал для записи истории
        history_add_coins_channel = client.get_channel(config.CHANNEL_ID_HISTORY_ADD_COINS)

        # Отправляем embed сообщение в дополнительный канал
        await history_add_coins_channel.send(embed=embed)

    else:
        await message.author.send(f"Статик {static_id} не найден в базе данных.")

async def ready():
    logger.info('Logged in as {0.user}'.format(client))
    # Initialize table and load user data from database
    await create_tables_if_not_exist()
    global guild
    guild = client.get_guild(config.GUILD_ID)
    # for role in guild.roles:
    #     logger.info(f"{role.name} - {role.id}")  # выводим имя и ID каждой роли
    logger.info("Bot administrators:")
    global bot_administrators
    bot_administrators = []
    for role in guild.roles:
        if role.id == config.ROLE_ID_TheRoyalFamily or role.id == config.ROLE_ID_TheHeadInnkeeper:
            for member in role.members:
                bot_administrators.append(member.id)
                logger.info(f"{member.id} | {member}")
    logger.info("Bot started!")

async def purge(uid, message):
    if uid not in bot_administrators:
        await message.author.send("У Вас нет прав для использования команды !purge.")
        if isinstance(message.channel, disnake.TextChannel):
            await message.delete()
        return
    try:
        await message.channel.purge(limit=50)
        await message.channel.send("Successfully deleted the last 50 messages.", delete_after=5.0)
    except Exception as e:
        await message.channel.send(f"An error occurred: {e}")

async def paid_check(uid, author, message):
    static_id = author.split("|")[1].strip() if "|" in author else None
    if static_id is None:
        await message.delete()
        await message.author.send(
            "Для того чтобы получить монету, необходимо указать static_id в никнейме пользователя. Например: Ahu Enen | 123456")
    elif await get_user_data(uid) and await get_user_data_by_static_id(static_id):
        await message.channel.set_permissions(message.author, send_messages=False)
        await message.delete()
        await message.author.send(f"{author}, вы уже получили свою монету!")
        server = message.guild
        role = discord.utils.get(server.roles, id=config.ROLE_ID_Guest)
        if role is not None:
            await message.author.add_roles(role)
    else:

        user_data = {}
        user_data[uid] = {"coins": 1, "static_id": static_id, "guest": True, "moderate": False, "vip": False}
        await save_user_data(user_data)

        server = message.guild
        # Добавляем роль "Guest" пользователю
        await message.author.add_roles(discord.utils.get(server.roles, id=config.ROLE_ID_Guest))
        # Добавляем роль "MODERATE" пользователю
        await message.author.add_roles(discord.utils.get(server.roles, id=config.ROLE_ID_MODERATE))

        # await message.channel.set_permissions(message.author, send_messages=False)
        await message.delete()
        await message.author.send(
            f"{author}, Вы получили свою монету и стали нашим Гостем. После проверки Вам будет доступен новый функционал!")
        await message.author.send(f"Подробнее в <#{config.CHANNEL_ID_MODERATE}>")
        await send_moderation_message(uid, static_id)

async def paid_vip_check(uid, author, message):
    user_data = {}
    user_data[uid] = await get_user_data(uid)
    if user_data[uid]["coins"] >= 10:
        # Добавляем роль "VIP Guest" пользователю
        server = message.author.guild
        role = discord.utils.get(server.roles, id=config.ROLE_ID_VIP)
        if role is not None:
            await message.author.add_roles(role)
        await message.channel.set_permissions(message.author, send_messages=False)
        await message.delete()
        user_data[uid]["coins"] -= 10
        await save_user_data(user_data)
        await message.author.send(
            f"{author}, Вы потратили 10 монет! Вы стали VIP! Теперь для Вас доступен новый функционал!")
        await message.author.send(f"Подробнее в <#{config.CHANNEL_ID_VIP_SERVICE_COST}>")
    else:
        await message.delete()
        await message.author.send(f"{author}, Кажется Вы не внесли взнос в размере 10 монет!")

async def send_moderation_message(uid, static_id):
    # Получаем канал для модерации
    channel = client.get_channel(config.CHANNEL_ID_MODERATE)
    if not channel:
        return

    # Создаем экземпляр класса `Button` для кнопки "Да"
    yes_button = disnake.ui.Button(
        label="Да",
        style=disnake.ButtonStyle.green
    )

    # Создаем экземпляр класса `Button` для кнопки "Нет"
    no_button = disnake.ui.Button(
        label="Нет",
        style=disnake.ButtonStyle.red
    )

    # Создаем экземпляр класса `ActionRow` и добавляем в него кнопки
    action_row = disnake.ui.ActionRow(yes_button, no_button)

    # Создаем экземпляр класса `Message` и отправляем его в канал
    message = await channel.send(
        "Вы уверены, что хотите продолжить?",
        components=[action_row]
    )

    # Создаем обработчик события нажатия на кнопку
    async def on_button_click(interaction: disnake.MessageInteraction):
        if interaction.component.label == "Да":
            await interaction.response.edit_message(content="Вы выбрали Да!")
        elif interaction.component.label == "Нет":
            await interaction.response.edit_message(content="Вы выбрали Нет!")
        await interaction.message.remove_reaction(interaction.component.label, interaction.user)

    # Добавляем обработчик на экземпляр класса `Message`
    disnake_bot.add_listener(on_button_click)

    # Возвращаем созданный экземпляр класса `Message`
    return message


