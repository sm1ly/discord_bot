import disnake
from disnake.ext import commands
from func.logger import logger
from main import bot_administrators


class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="purge", description="Удаляет последние 50 сообщений в канале")
    async def purge(self, inter: disnake.ApplicationCommandInteraction):
        if inter.author.id not in bot_administrators:
            await inter.response.send_message("У Вас нет прав для использования команды !purge.", ephemeral=True)
            return
        try:
            await inter.channel.purge(limit=50)
            await inter.response.send_message("Successfully deleted the last 50 messages.", ephemeral=True, delete_after=5.0)
        except Exception as e:
            logger.error(f"An error occurred: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(Purge(bot))
