# Import the necessary libraries.
import disnake
from disnake.ext import commands
import config
from func.logger import logger
from func.database import create_tables_if_not_exist, drop_table


# Creating a commands.Bot() instance, and assigning it to "bot"
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(intents=disnake.Intents.all(), command_prefix="/", command_sync_flags=command_sync_flags)

# Define the bot_administrators list
bot_administrators = []


# When the bot is ready, run this code.
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    # Initialize table and load user data from database
    # await drop_table()
    await create_tables_if_not_exist()
    logger.info("Bot administrators:")
    trg = bot.get_guild(config.GUILD_ID)
    for role in trg.roles:
        if role.id == config.ROLE_ID_TheRoyalFamily or role.id == config.ROLE_ID_TheHeadInnkeeper:
            for member in role.members:
                bot_administrators.append(member.id)
                logger.info(f"{member.id} | {member}")
    logger.info("Bot started!")


bot.load_extension("cogs.AddCoins")
bot.load_extension("cogs.BotMenu")
bot.load_extension("cogs.CheckBalance")
bot.load_extension("cogs.CheckStaticBalance")
bot.load_extension("cogs.PaidCheck")
bot.load_extension("cogs.Purge")
bot.load_extension("cogs.Threader")
bot.load_extension("cogs.VipPaidCheck")
bot.run(config.token)
