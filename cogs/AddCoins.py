import disnake
from datetime import datetime
from disnake.ext import commands
from func.logger import logger
from func.generate_random_color import generate_random_color
from main import bot_administrators
from database import get_user_data, get_user_data_by_static_id, save_user_data, \
    save_user_data_by_static_id
from config import CHANNEL_ID_HISTORY_ADD_COINS
import sys


class AddCoins(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="add_coins", description="Добавляет монеты выбранному статику. Usage: /add_coins <static_id> <amount>")
    async def add_coins(self, inter: disnake.ApplicationCommandInteraction,
                        static_id: int = commands.Param(gt=0, description='ID статика'),
                        amount: int = commands.Param(gt=0, description='Количество монет')):
        if inter.author.id not in bot_administrators:
            await inter.response.send_message("У Вас нет прав для использования команды /add_coins.", ephemeral=True)
            return
        try:
            static_id = str(static_id)
            print("1", static_id)
            user_data = await get_user_data_by_static_id(static_id)
            print("2", static_id)
            if user_data:
                print("3", static_id)
                print("UD1:", user_data)
                user_data["coins"] += amount
                print("UD2:", user_data)
                await save_user_data_by_static_id(user_data)
                await inter.response.send_message(f"Успешно добавлено {amount} монет статику {static_id}!", ephemeral=True)

                # # Получаем текущую дату и время
                # current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #
                # # Создаем embed сообщение
                # color = generate_random_color()
                # embed = disnake.Embed(title='Начисление монет', color=color)
                # embed.add_field(name='Кто', value=f'<@{uid}>', inline=False)
                # embed.add_field(name='Кому', value=f'<@{user_data["uid"]}>', inline=False)
                # embed.add_field(name='Статик', value=f'{static_id}', inline=False)
                # embed.add_field(name='Сколько монет', value=amount, inline=False)
                # embed.add_field(name='Дата и время', value=current_time, inline=False)
                #
                # # Получаем дополнительный канал для записи истории
                # history_add_coins_channel = client.get_channel(CHANNEL_ID_HISTORY_ADD_COINS)
                #
                # # Отправляем embed сообщение в дополнительный канал
                # await history_add_coins_channel.send(embed=embed)

            else:
                await inter.response.send_message(f"Статик {static_id} не найден в базе данных.", ephemeral=True)
        except Exception as e:
            calling_function_name = sys._getframe(1).f_code.co_name
            logger.error(f"Error in {calling_function_name}: {str(e)}")


def setup(bot: commands.Bot):
    bot.add_cog(AddCoins(bot))
