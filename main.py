import base64
import os

import nextcord
from nextcord.ext import commands

import config

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)





# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


# Load your cogs here
load_cogs()
loaded_cogs = [filename[:-3] for filename in os.listdir('cogs') if filename.endswith('.py')]
print(f'Loaded cogs: {", ".join(loaded_cogs)}')

bot.run(config.BOT_TOKEN)