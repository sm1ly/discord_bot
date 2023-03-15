import disnake
from disnake.ext import commands
from disnake import Embed
from func.logger import logger
from func.database import get_user_data, is_user_moderated, is_user_vip
from bot import bot_administrators
from config import CHANNEL_ID_HOW_WE_WORK, CHANNEL_ID_MODERATE, CHANNEL_ID_PAID_SERVICE, \
    ROLE_ID_VIP, GUILD_ID, COLOR_VIP


def create_button(label, emoji, custom_id, disabled=False, row=None, style=disnake.ButtonStyle.grey):
    class CustomButton(disnake.ui.Button):
        def __init__(self):
            super().__init__(label=label, emoji=emoji, custom_id=custom_id, disabled=disabled, row=row, style=style)

        async def callback(self, inter: disnake.MessageInteraction):
            choice = self.label.split("|")[0].strip()
            await inter.response.send_message(f"Вы выбрали: {choice}")

    return CustomButton()


# Создаем новый класс кнопки DisableVipButton
# class DisableVipButton(disnake.ui.Button):
#     def __init__(self):
#         super().__init__(label="Отключить VIP", custom_id="disable_vip", row=4, style=disnake.ButtonStyle.red)
#
#     async def callback(self, inter: disnake.MessageInteraction):
#         # Удаляем роль с ID ROLE_ID_VIP
#         guild = await inter.client.fetch_guild(GUILD_ID)
#         role_to_remove = guild.get_role(ROLE_ID_VIP)
#         member = await guild.fetch_member(inter.author.id)
#         if role_to_remove in member.roles:
#             await member.remove_roles(role_to_remove)
#
#         await disable_vip(inter.author.id)
#         await inter.response.send_message("Ваш VIP статус был отключен")


def create_buttons_view(buttons):
    class ButtonsView(disnake.ui.View):
        def __init__(self):
            super().__init__()
            for button in buttons:
                self.add_item(button)

    return ButtonsView()


class BotMenu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info(f"loaded cog: {self.qualified_name}")

    @commands.slash_command(name="menu", description="Вызов меню доступных услуг.")
    async def menu(self, inter: disnake.ApplicationCommandInteraction):
        user_data = {inter.author.id: await get_user_data(inter.author.id)}
        if not user_data.get(inter.author.id):
            await inter.response.send_message(
                f'Вы не являетесь нашим Гостем или VIP-Гостем. Подробнее в <#{CHANNEL_ID_HOW_WE_WORK}>.',
                ephemeral=True)
            return

        is_vip = await is_user_vip(inter.author.id)
        is_moderated = await is_user_moderated(inter.author.id)

        if is_vip or is_moderated:
            buttons = [
                create_button("Организация транспортировки | 2 монеты", "\U0001F6E1\uFE0F", "pos1", row=0,
                              style=disnake.ButtonStyle.primary),
                create_button("Услуги консьержа 24/7 | 1 монета", "\U0001F468\u200D\u2708\uFE0F", "pos2", row=0,
                              style=disnake.ButtonStyle.primary),
                create_button("Юридическая помощь | 1 монета", "\U0001F31F", "pos3", row=1,
                              style=disnake.ButtonStyle.success),
                create_button("Услуги аренды спортивного инвентаря | Индивидуально", "\U0001F52B", "pos4",
                              disabled=not is_vip, row=1, style=disnake.ButtonStyle.primary),
                create_button("Сервис удаления персональных данных | 10 монет", "\U0001F510", "pos5",
                              disabled=not is_vip, row=2, style=disnake.ButtonStyle.success),
                create_button("Эксклюзивные вечеринки | 10 монет", "\U000026B0\uFE0F", "pos6",
                              disabled=not is_vip, row=2, style=disnake.ButtonStyle.danger),
                create_button("Специальные мероприятия | 10 монет", "\U0001F3AF", "pos7",
                              disabled=not is_vip, row=3, style=disnake.ButtonStyle.danger),
            ]
            # Добавляем кнопку Disable VIP только для VIP-гостей
            # if is_vip:
            #     buttons.append(DisableVipButton())

            view = create_buttons_view(buttons)

            if is_vip:
                await inter.response.send_message(f'Вам доступны следующие услуги:', view=view, ephemeral=True)
            else:
                await inter.response.send_message(f'Вам доступны следующие услуги:', view=view, ephemeral=True)
                # Создаем и отправляем embed-сообщение
                color = int(COLOR_VIP.format(), 16)
                embed = Embed(title="", description="Для получения дополнительных услуг станьте VIP.",
                              color=color)
                embed.add_field(name='\u200B', value=f'Подробнее в <#{CHANNEL_ID_HOW_WE_WORK}>.', inline=False)
                await inter.followup.send(embed=embed, ephemeral=True)

        else:
            await inter.response.send_message(f'Вы еще не прошли проверку. Подробнее в <#{CHANNEL_ID_MODERATE}>.',
                                              ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(BotMenu(bot))
