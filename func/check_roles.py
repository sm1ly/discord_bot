import disnake
from config import CHANNEL_ID_I_PAID, REACTION_SYMBOL, CHANNEL_ID_MODERATE, ROLE_ID_Guest, \
    ROLE_ID_MODERATE, GUILD_ID, COLOR_success, COLOR_danger, COLOR_primary
from disnake.ext import commands
from func.logger import logger
from func.database import get_user_data, get_user_data_by_static_id, save_user_data, \
    save_user_data_by_static_id, remove_user, set_user_moderate
from disnake.ui import View, button
from bot import bot_administrators
from func.generate_random_color import generate_random_color


async def check_roles(uid):
    ROLE_ID_MODERATE = 12345
    ROLE_ID_GUEST = 23456
    ROLE_ID_VIP = 34567

    for role in member.roles:
        if role.id not in [ROLE_ID_MODERATE, ROLE_ID_GUEST, ROLE_ID_VIP]:
            return True

    return False