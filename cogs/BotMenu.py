import disnake
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data, is_user_moderated, is_user_vip
from bot import bot_administrators
from config import CHANNEL_ID_HOW_WE_WORK, CHANNEL_ID_MODERATE, CHANNEL_ID_PAID_SERVICE


def create_dropdown(options):
    class Dropdown(disnake.ui.StringSelect):
        def __init__(self):
            super().__init__(
                placeholder="Выберите позицию...",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            await inter.response.send_message(f"Вы выбрали: {self.values[0]}")

    return Dropdown()


def create_dropdown_view(dropdown):
    class DropdownView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(dropdown)

    return DropdownView()


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

        guest_options = [
            disnake.SelectOption(label="Организация транспортировки гостей и их личных вещей"),
            disnake.SelectOption(label="Услуги консьержа 24/7"),
            disnake.SelectOption(label="Юридическая помощь"),
        ]

        vip_options = [
            disnake.SelectOption(label="pos1", description="This is pos1", emoji="🥇"),
            disnake.SelectOption(label="pos2", description="This is pos2", emoji="🥈"),
            disnake.SelectOption(label="pos3", description="This is pos3", emoji="🥉"),
            disnake.SelectOption(label="pos4", description="This is pos4", emoji="🏅"),
            disnake.SelectOption(label="pos5", description="This is pos5", emoji="🎖️"),
            disnake.SelectOption(label="pos6", description="This is pos6", emoji="🏆"),
            disnake.SelectOption(label="pos7", description="This is pos7", emoji="🎗️"),
        ]

        if await is_user_vip(inter.author.id):
            vip_dropdown = create_dropdown(vip_options)
            vip_menu = create_dropdown_view(vip_dropdown)
            await inter.response.send_message(f'VIP Guest menu', view=vip_menu, ephemeral=True)
            return

        if await is_user_moderated(inter.author.id):
            guest_dropdown = create_dropdown(guest_options)
            guest_menu = create_dropdown_view(guest_dropdown)
            await inter.response.send_message(f'Guest menu', view=guest_menu, ephemeral=True)
        else:
            await inter.response.send_message(f'Вы еще не прошли проверку. Подробнее в <#{CHANNEL_ID_MODERATE}>.',
                                              ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(BotMenu(bot))

