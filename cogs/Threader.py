import disnake
from disnake.ext import commands
from config import CHANNEL_ID_PAID_SERVICE, GUILD_ID, ROLE_ID_TheHeadInnkeeper, ROLE_ID_TheRoyalFamily, \
    ROLE_ID_Courier, ROLE_ID_Security, ROLE_ID_Technician, ROLE_ID_Concierge, ROLE_ID_Porter, \
    ROLE_ID_Briber, ROLE_ID_Merchant, ROLE_ID_Hacker, ROLE_ID_Blackmailer, ROLE_ID_Don, ROLE_ID_MAPPING
from func.database import get_user_data, save_user_data, get_service_data
from func.logger import logger
from datetime import datetime


class Threader(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    async def start_thread(self, inter: disnake.MessageInteraction, custom_id: str):
        uid = inter.user.id
        user_data = {uid: await get_user_data(uid)}
        service_data = await get_service_data(custom_id)
        if not service_data:
            return  # Ничего не делать, если данные услуги не найдены

        local_name, roles, price = service_data
        static_id = user_data[uid]["static_id"]
        user_data[uid]["coins"] -= price
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await save_user_data(user_data)
        channel = self.bot.get_channel(CHANNEL_ID_PAID_SERVICE)
        thread = await channel.create_thread(name=f"Услуга: {local_name} | Статик: {static_id} | Дата: {current_time}", reason="Новый заказ",
                                             type=disnake.ChannelType.public_thread, invitable=False)
        user_mention = inter.user.mention
        await thread.send(f"{user_mention}, Поздравляем, Вы купили: {local_name}.\nВ чат добавлены:")
        guild = self.bot.get_guild(GUILD_ID)  # Получаем объект сервера с использованием GUILD_ID
        role_ids = [ROLE_ID_MAPPING[role_name] for role_name in roles]
        for role_id in role_ids:  # Используйте role_ids вместо roles
            role = guild.get_role(role_id)  # Получаем объект роли по ID
            await thread.send(role.mention)  # Теперь используем атрибут mention объекта роли
        balance = user_data[uid]["coins"]
        await thread.send(f"У Вас осталось {balance} монет.")


def setup(bot: commands.Bot):
    bot.add_cog(Threader(bot))
