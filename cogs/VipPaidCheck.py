import disnake
from config import CHANNEL_ID_I_PAID_VIP, REACTION_SYMBOL, CHANNEL_ID_MODERATE, ROLE_ID_VIP, GUILD_ID, \
    CHANNEL_ID_VIP_SERVICE_COST, CHANNEL_ID_HISTORY_BECOME_VIP, COLOR_VIP
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data, get_user_data_by_static_id, save_user_data, \
    save_user_data_by_static_id, set_user_vip
from datetime import datetime


class VipPaidCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.channel.id == CHANNEL_ID_I_PAID_VIP and message.content.startswith(REACTION_SYMBOL):
            logger.info(f'{message.author} [{message.author.display_name}]: {message.content}')
            if isinstance(message.channel, disnake.TextChannel):
                await message.delete()

            user_data = {message.author.id: await get_user_data(message.author.id)}
            if user_data.get(message.author.id)["coins"] >= 10:
                guild = self.bot.get_guild(GUILD_ID)
                # Добавляем роль "VIP Guest" пользователю
                await message.author.add_roles(disnake.utils.get(guild.roles, id=ROLE_ID_VIP))
                await message.channel.set_permissions(message.author, send_messages=False)
                user_data[message.author.id]["coins"] -= 10
                await save_user_data(user_data)
                await message.author.send(
                    f"{message.author.display_name}, Вы потратили 10 монет! Вы стали VIP! Теперь для Вас доступен новый функционал!")
                await message.author.send(f"Подробнее в <#{CHANNEL_ID_VIP_SERVICE_COST}>")
                await set_user_vip(message.author.id)

                # Получаем текущую дату и время
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Создаем embed сообщение
                color = int(COLOR_VIP.format(), 16)
                embed = disnake.Embed(title='Become VIP', color=color)
                embed.add_field(name='Кто', value=f'<@{message.author.id}>', inline=False)
                embed.add_field(name='Статик', value=f'{user_data[message.author.id]["static_id"]}', inline=False)
                embed.add_field(name='Дата и время', value=current_time, inline=False)

                # Получаем дополнительный канал для записи истории
                history_become_vip_channel = self.bot.get_channel(CHANNEL_ID_HISTORY_BECOME_VIP)

                # Отправляем embed сообщение в дополнительный канал
                await history_become_vip_channel.send(embed=embed)
            else:
                await message.author.send(f"{message.author.display_name}, Кажется Вы не внесли взнос в размере 10 монет!")


def setup(bot: commands.Bot):
    bot.add_cog(VipPaidCheck(bot))
