import nextcord
from nextcord import Interaction
from nextcord.ext import commands, tasks
import sqlite3


class NarutoWhisperLogic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='whisper')
    async def whisper(self, interactions: Interaction, *, message: str):
        # Connect to the SQLite database
        conn = sqlite3.connect(f"database/serverid-{interactions.guild.id}_database.db")
        # NOTE: The above step just creates a connection. You might want to perform
        # operations with the database, like storing or retrieving data.

        # Closing the connection after usage
        conn.close()

        # Check if the roles exist in the guild
        lore_writer = nextcord.utils.get(interactions.guild.roles, name="Lore Writer")
        lore_manager = nextcord.utils.get(interactions.guild.roles, name="Lore Manager")

        if not lore_writer or not lore_manager:
            await interactions.send("The roles 'Lore Writer' or 'Lore Manager' do not exist in this guild.")
            return

        # Create a private thread
        thread = await interactions.channel.create_thread(
            name=f"Private-Action-{interactions.user.name}",
            type=nextcord.ChannelType.private_thread)

        await thread.add_user(interactions.user)
        await thread.add_user(lore_writer)
        await thread.add_user(lore_manager)

        await thread.send(f"{interactions.user.mention} private action: {message}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("NarutoWhisperLogic cog is ready!")


def setup(bot):
    bot.add_cog(NarutoWhisperLogic(bot))
