import disnake
from datetime import datetime
from disnake.ext import commands
from func.logger import logger
from func.generate_random_color import generate_random_color
from bot import bot_administrators
from func.database import get_user_data, get_user_data_by_static_id, save_user_data, \
    save_user_data_by_static_id
from config import CHANNEL_ID_HISTORY_ADD_COINS


class AddCoins(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="add_coins", description="Добавляет монеты выбранному статику.")
    async def add_coins(self, inter: disnake.ApplicationCommandInteraction,
                        static_id: int = commands.Param(gt=0, description='ID статика'),
                        amount: int = commands.Param(gt=0, description='Количество монет')):
        if inter.author.id not in bot_administrators:
            await inter.response.send_message("У Вас нет прав для использования команды /add_coins.", ephemeral=True)
            return
        user_data = {static_id: await get_user_data_by_static_id(static_id)}
        if user_data.get(static_id):
            user_data[static_id]["coins"] += amount
            await save_user_data_by_static_id(user_data)
            await inter.response.send_message(f"Успешно добавлено {amount} монет статику {static_id}!", ephemeral=True)

            # Получаем текущую дату и время
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Создаем embed сообщение
            color = generate_random_color()
            embed = disnake.Embed(title='Начисление монет', color=color)
            embed.add_field(name='Кто', value=f'<@{inter.author.id}>', inline=False)
            embed.add_field(name='Кому', value=f'<@{user_data[static_id]["uid"]}>', inline=False)
            embed.add_field(name='Статик', value=f'{static_id}', inline=False)
            embed.add_field(name='Сколько монет', value=amount, inline=False)
            embed.add_field(name='Дата и время', value=current_time, inline=False)

            # Получаем дополнительный канал для записи истории
            history_add_coins_channel = self.bot.get_channel(CHANNEL_ID_HISTORY_ADD_COINS)

            # Отправляем embed сообщение в дополнительный канал
            await history_add_coins_channel.send(embed=embed)

        else:
            await inter.response.send_message(f"Статик {static_id} не найден в базе данных.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(AddCoins(bot))
