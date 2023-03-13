import disnake
from config import CHANNEL_ID_I_PAID, REACTION_SYMBOL, CHANNEL_ID_MODERATE, ROLE_ID_Guest, \
    ROLE_ID_MODERATE, GUILD_ID, COLOR_success, COLOR_danger, COLOR_primary
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data, get_user_data_by_static_id, save_user_data, \
    save_user_data_by_static_id
from disnake.ui import View, button
from bot import bot_administrators
from func.generate_random_color import generate_random_color


class ModerateButton(View):
    def __init__(self, moderate_uid, embed_moderate):
        super().__init__()
        self.moderate_uid = moderate_uid
        self.embed_moderate = embed_moderate

    @button(label="YES", style=disnake.ButtonStyle.success)
    async def moderate_button_yes(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id not in bot_administrators:
            await interaction.response.send_message("У Вас нет прав нажимать на эту кнопку.", ephemeral=True)
            return
        self.embed_moderate.title = 'ДА'
        color_success = int(COLOR_success.format(), 16)
        self.embed_moderate.color = color_success
        await interaction.response.edit_message(embed=self.embed_moderate, view=None)
        # self.stop()

    @button(label="NO", style=disnake.ButtonStyle.danger)
    async def moderate_button_no(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id not in bot_administrators:
            await interaction.response.send_message("У Вас нет прав нажимать на эту кнопку.", ephemeral=True)
            return
        self.embed_moderate.title = 'Нет | Изгнан'
        color_danger = int(COLOR_danger.format(), 16)
        self.embed_moderate.color = color_danger
        await interaction.response.edit_message(embed=self.embed_moderate, view=None)
        guild = await interaction.client.fetch_guild(GUILD_ID)
        member = await guild.fetch_member(self.moderate_uid)
        if member:
            # Создаем embed сообщение
            color = generate_random_color()
            embed_kick = disnake.Embed(title='Вас Изгнали.', color=color)
            embed_kick.add_field(name='\u200B', value="""Позвольте мне представить величественную картину, которая развернулась перед моими глазами. Пятеро громадных амбалов, как в греческой мифологии, мощными телами и устрашающими чертами лица, свирепо вытолкнули Вас из священных стен элитного отеля "The Royal Game".
            
            Это было зрелище, которое нельзя забыть. Мощный и дерзкий, этот акт принес вечную память о героических усилиях этих амбалов, которые настаивали на своих правах и не желали ими жертвовать. Их сила и могущество были непоколебимы, и они использовали их, чтобы защитить свой дом от нежелательных гостей.""", inline=False)
            # \u200B Вы Нарушили.
            embed_kick.add_field(name="\u200B", value="""Но, возможно, Вы, уважаемый собеседник, нарушили некоторые правила поведения, пренебрегли этикетом и не уважили привилегии, предоставленные Вам в этом роскошном отеле. Именно поэтому эти амбалы, будучи стражами порядка и справедливости, приняли такие жесткие меры, чтобы защитить свой дом от Вашего непочтительного поведения.
            
            Так что вспомните этот день, уважаемый собеседник, как день, когда Вы столкнулись с истинной мощью и силой, когда Вы поняли, что элитный отель "The Royal Game" не просто так называется "королевской игрой". И пусть это неприятное событие станет для Вас незабываемым уроком в уважении к другим и в общении с окружающими.""", inline=False)
            await member.send(embed=embed_kick)
            await member.kick(reason="Kicked by CTL | FOR THE GLORY !")
            # self.stop()


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
                guild = self.bot.get_guild(GUILD_ID)
                # Добавляем роль "Guest" пользователю
                role = disnake.utils.get(guild.roles, id=ROLE_ID_Guest)
                if role is not None:
                    await message.author.add_roles(role)
            else:
                user_data = {message.author.id: {"coins": 1, "static_id": static_id, "guest": True, "moderate": False, "vip": False}}
                await save_user_data(user_data)

                # await message.channel.set_permissions(message.author, send_messages=False)
                guild = self.bot.get_guild(GUILD_ID)
                # Добавляем роль "Guest" пользователю
                await message.author.add_roles(disnake.utils.get(guild.roles, id=ROLE_ID_Guest))
                # Добавляем роль "MODERATE" пользователю
                await message.author.add_roles(disnake.utils.get(guild.roles, id=ROLE_ID_MODERATE))

                await message.author.send(f"{message.author.display_name}, Вы получили свою монету и стали нашим Гостем. После проверки Вам будет доступен новый функционал!")
                await message.author.send(f"Подробнее в <#{CHANNEL_ID_MODERATE}>")

                # Создаем embed сообщение
                color_primary = int(COLOR_primary.format(), 16)
                embed_moderate = disnake.Embed(title='Заплатил за 1 монету?', color=color_primary)
                embed_moderate.add_field(name='Кто', value=f'<@{message.author.id}>', inline=False)
                embed_moderate.add_field(name='Статик', value=f'{user_data[message.author.id]["static_id"]}', inline=False)

                moderate_channel = self.bot.get_channel(CHANNEL_ID_MODERATE)
                moderate_uid = message.author.id
                # msg = await moderate_channel.send(embed=embed_moderate, view=ModerateButton(moderate_uid, msg))
                await moderate_channel.send(embed=embed_moderate, view=ModerateButton(moderate_uid, embed_moderate))

        elif isinstance(message.channel, disnake.DMChannel) and message.content.startswith(REACTION_SYMBOL):
            logger.info(f'{message.author} [{message.author.display_name}]: {message.content}')
            await message.author.send(f"{message.author.display_name}, невозможно получить монету в личных сообщениях. Пройдите в <#{CHANNEL_ID_I_PAID}> и поставьте `+`")


def setup(bot: commands.Bot):
    bot.add_cog(PaidCheck(bot))
