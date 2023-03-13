import disnake
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data_by_static_id
from bot import bot_administrators


class CheckStaticBalance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="check_static_balance", description="Проверить баланс статика")
    async def check_static_balance(self, inter: disnake.ApplicationCommandInteraction,
                                   static_id: int = commands.Param(gt=0, description='ID статика')):
        if inter.author.id not in bot_administrators:
            await inter.response.send_message("У Вас нет прав для использования команды /add_coins.", ephemeral=True)
            return
        user_data = {static_id: await get_user_data_by_static_id(static_id)}
        if not user_data.get(static_id):
            await inter.response.send_message(f"{inter.author.display_name}, у статика {static_id} нет баланса.",
                                              ephemeral=True)
            return
        else:
            balance = user_data[static_id]["coins"]
            await inter.response.send_message(f"{inter.author.display_name}, баланс {static_id} : {balance} монет.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(CheckStaticBalance(bot))
