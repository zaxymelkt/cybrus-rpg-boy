import base64

import nextcord
from nextcord.ext import commands

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

base64_encoded_string = "TVRFME5EZ3dNVEV4TURVMU56Y3lPRGM0T0EuR1N1UWxkLlJlQVY4TmtMMWwwNjFCakJsSHpGR2p1eFZPZG9IZDVETWVFQXR3"

# Decode the base64-encoded string
decoded_bytes = base64.b64decode(base64_encoded_string)
decoded_string = decoded_bytes.decode('utf-8')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('it worked')


bot.run(decoded_string)
