import disnake
from config import CHANNEL_ID_I_PAID, REACTION_SYMBOL, CHANNEL_ID_MODERATE, ROLE_ID_Guest, \
    ROLE_ID_MODERATE
from disnake.ext import commands
from func.logger import logger
from database import get_user_data, get_user_data_by_static_id, save_user_data, \
    save_user_data_by_static_id


# class MyBtn(View):
#     def __init__(self):
#         super().__init__()
#
#     @button(label="btn1")
#     async def first_btn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
#         await interaction.response.send_message("what are u doing?")
#
#     @button(label="btn2")
#     async def second_btn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
#         await interaction.response.send_message("what are u doing? x2")


class PaidCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.channel.id == CHANNEL_ID_I_PAID and message.content.startswith(REACTION_SYMBOL):
            logger.info(f'{message.author} [{message.author.display_name}]: {message.content}')
            if isinstance(message.channel, disnake.TextChannel):
                await message.delete()
            static_id = message.author.display_name.split("|")[1].strip() if "|" in message.author.display_name else None
            if static_id is None:
                await message.author.send("Для того чтобы получить монету, необходимо указать static_id в никнейме пользователя. Например: Ahu Enen | 123456")
            elif await get_user_data(message.author.id) and await get_user_data_by_static_id(static_id):
                # await message.channel.set_permissions(message.author, send_messages=False)
                await message.author.send(f"{message.author.display_name}, вы уже получили свою монету!")
                server = test_guilds
                role = disnake.utils.get(server.roles, id=config.ROLE_ID_Guest)
                if role is not None:
                    await message.author.add_roles(role)
            else:
                user_data = {message.author.id: {"coins": 1, "static_id": static_id, "guest": True, "moderate": False, "vip": False}}
                await save_user_data(user_data)

                server = message.guild
                # Добавляем роль "Guest" пользователю
                await message.author.add_roles(disnake.utils.get(server.roles, id=ROLE_ID_Guest))
                # Добавляем роль "MODERATE" пользователю
                await message.author.add_roles(disnake.utils.get(server.roles, id=ROLE_ID_MODERATE))

                # await message.channel.set_permissions(message.author, send_messages=False)
                await message.author.send(f"{message.author.display_name}, Вы получили свою монету и стали нашим Гостем. После проверки Вам будет доступен новый функционал!")
                await message.author.send(f"Подробнее в <#{CHANNEL_ID_MODERATE}>")

        elif isinstance(message.channel, disnake.DMChannel) and message.content.startswith(REACTION_SYMBOL):
            logger.info(f'{message.author} [{message.author.display_name}]: {message.content}')
            await message.author.send(f"{message.author.display_name}, невозможно получить монету в личных сообщениях. Пройдите в <#{CHANNEL_ID_I_PAID}> и поставьте `+`")

# TODO add moderation here


def setup(bot: commands.Bot):
    bot.add_cog(PaidCheck(bot))
