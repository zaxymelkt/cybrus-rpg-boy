import nextcord
from nextcord.ext import commands
import sqlite3


async def repost_with_fake_profile(interactions, message, clan, oc_url):
    # Create an embed message to mimic the appearance of a Discord message
    embed = nextcord.Embed(description=message, color=0x7289DA)
    embed.set_author(name=clan, icon_url=oc_url)  # Set author (character's clan) and profile picture (oc_url)

    # Send the modified message as an embed
    await interactions.send(embed=embed, allowed_mentions=nextcord.AllowedMentions.none())


def get_character_info(server_id, user_id):
    try:
        db_name = f'database/serverid-{server_id}_database.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Fetch character information from the database
        cursor.execute("SELECT clan, oc_url FROM personal_info WHERE user_id=?", (user_id,))
        character_info = cursor.fetchone()

        conn.close()

        return character_info

    except sqlite3.Error as err:
        print(f"Error fetching character information: {err}")
        return None


class NarutoEmoteFunction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='emote')
    async def emote_command(self, interactions: nextcord.Interaction, message: str):
        user_id = interactions.user.id
        server_id = interactions.guild.id

        # Fetch character information from the database based on user_id
        character_info = get_character_info(server_id, user_id)

        if character_info is not None:
            # Get the character's clan and oc_url
            clan, oc_url = character_info

            # Modify and repost the user's message with a fake profile appearance
            await repost_with_fake_profile(interactions, message, clan, oc_url)
        else:
            await interactions.send("Character information not found. Please create your character using '/create_oc'.")


def setup(bot):
    bot.add_cog(NarutoEmoteFunction(bot))
