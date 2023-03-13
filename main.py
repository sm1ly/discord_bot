# Import the necessary libraries.
import disnake
from disnake.ext import commands
import config
from func.logger import logger
from database import create_tables_if_not_exist, drop_table


# Creating a commands.Bot() instance, and assigning it to "bot"
bot = commands.Bot(intents=disnake.Intents.all(), command_prefix="/")

# Define the bot_administrators list
bot_administrators = []


# When the bot is ready, run this code.
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    # Initialize table and load user data from database
    await drop_table()
    await create_tables_if_not_exist()
    guild = bot.get_guild(config.GUILD_ID)
    logger.info("Bot administrators:")
    for role in guild.roles:
        if role.id == config.ROLE_ID_TheRoyalFamily or role.id == config.ROLE_ID_TheHeadInnkeeper:
            for member in role.members:
                bot_administrators.append(member.id)
                logger.info(f"{member.id} | {member}")
    logger.info("Bot started!")


# обработчик ошибок
@bot.event
async def on_command_error(ctx, error):
    # логируем ошибки
    logger.error(f'Ошибка в команде {ctx.command}: {error}', exc_info=error)

bot.load_extension("cogs.PaidCheck")
bot.load_extension("cogs.Purge")
bot.load_extension("cogs.AddCoins")
bot.run(config.token)