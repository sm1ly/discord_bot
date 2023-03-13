import disnake
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data

class CheckBalance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="check_balance", description="Проверить свой баланс")
    async def check_balance(self, inter: disnake.ApplicationCommandInteraction):
            user_data = await get_user_data(inter.author.id)
            if not user_data:
                await inter.response.send_message(f"{inter.author.display_name}, у Вас нет баланса, видимо Вы не оплатили ни одной монеты.", ephemeral=True)
                return

            balance = user_data["coins"]
            await inter.response.send_message(f"{inter.author.display_name}, Ваш баланс: {balance} монет.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(CheckBalance(bot))
