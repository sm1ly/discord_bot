#!/usr/bin/python3

async def interactions(interaction):
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