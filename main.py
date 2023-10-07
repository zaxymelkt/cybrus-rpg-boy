import nextcord
from nextcord.ext import commands
import sqlite3

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load the "NarutoBotJoin" cog
bot.load_extension('cogs.naruto_bot_join')
bot.load_extension('cogs.emote_function')
bot.load_extension('cogs.naruto_character_edit_logic')
bot.load_extension('cogs.naruto_whisper_logic')
bot.load_extension('cogs.naruto_statupdate_logic')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('it worked')



bot.run('MTE0NDgwMTExMDU1NzcyODc4OA.GtBQQq.O64tl5hvvZjJ7uSxaEPKitxMy2nxrCYetuYPfc')
