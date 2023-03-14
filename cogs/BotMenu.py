import disnake
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data, is_user_moderated, is_user_vip
from bot import bot_administrators
from config import CHANNEL_ID_HOW_WE_WORK, CHANNEL_ID_MODERATE, CHANNEL_ID_PAID_SERVICE


class BotMenu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="menu", description="Вызвать меню покупок услуг.")
    async def menu(self, inter: disnake.ApplicationCommandInteraction):
        user_data = {inter.author.id: await get_user_data(inter.author.id)}
        if not user_data.get(inter.author.id):
            await inter.response.send_message(
                f'Вы не являетесь нашим Гостем или VIP-Гостем. Подробнее в <#{CHANNEL_ID_HOW_WE_WORK}>.',
                ephemeral=True)
            return

        # если гость, moderated, vip - показываем вип меню
        if await is_user_vip(inter.author.id):
            await inter.response.send_message(f'VIP Guest menu', ephemeral=True)
            return

        # если гость, moderated - показываем меню
        if await is_user_moderated(inter.author.id):
            await inter.response.send_message(f'Guest menu', ephemeral=True)
        # если гость, но не moderated - не показываем меню
        else:
            await inter.response.send_message(f'Вы еще не прошли проверку. Подробнее в <#{CHANNEL_ID_MODERATE}>.',
                                              ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(BotMenu(bot))



# old working code
# import disnake
# from disnake.ext import commands
# from func.logger import logger
# from func.database import get_user_data, is_user_moderated, is_user_vip
# from bot import bot_administrators
# from config import CHANNEL_ID_HOW_WE_WORK, CHANNEL_ID_MODERATE, CHANNEL_ID_PAID_SERVICE
#
#
# class BotMenu(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         logger.info(f"loaded cog: {self.qualified_name}")
#
#     @commands.slash_command(name="menu", description="Вызвать меню покупок услуг.")
#     async def menu(self, inter: disnake.ApplicationCommandInteraction):
#         user_data = {inter.author.id: await get_user_data(inter.author.id)}
#         if not user_data.get(inter.author.id):
#             await inter.response.send_message(
#                 f'Вы не являетесь нашим Гостем или VIP-Гостем. Подробнее в <#{CHANNEL_ID_HOW_WE_WORK}>.',
#                 ephemeral=True)
#             return
#
#         # если гость, moderated, vip - показываем вип меню
#         if await is_user_vip(inter.author.id):
#             await inter.response.send_message(f'VIP Guest menu', ephemeral=True)
#             return
#
#         # если гость, moderated - показываем меню
#         if await is_user_moderated(inter.author.id):
#             await inter.response.send_message(f'Guest menu', ephemeral=True)
#         # если гость, но не moderated - не показываем меню
#         else:
#             await inter.response.send_message(f'Вы еще не прошли проверку. Подробнее в <#{CHANNEL_ID_MODERATE}>.',
#                                               ephemeral=True)
#
#
# def setup(bot: commands.Bot):
#     bot.add_cog(BotMenu(bot))
