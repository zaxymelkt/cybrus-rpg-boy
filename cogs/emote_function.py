import sqlite3
import re
from typing import Optional, Dict
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption


def extract_attributes(args: Optional[str]) -> Dict[str, Optional[str]]:
    attributes = {
        "Agility": None,
        "Taijutsu": None,
        "Endurance": None,
        "Intelligence": None,
        "Potency": None,
    }

    if args:
        # Split the args string by spaces to separate individual attributes
        attribute_list = args.split()

        for attribute in attribute_list:
            # Split each attribute by ':' to separate the name and value
            parts = attribute.split(':')

            if len(parts) == 2:
                name, value = parts[0], parts[1]

                # Check if the value contains a mathematical expression
                if re.match(r'^[\d+\-*/()\s]+$', value):
                    try:
                        # Evaluate the mathematical expression and convert the result to a string
                        result = str(eval(value))
                        attributes[name] = result
                    except Exception as e:
                        print(f"Error evaluating expression '{value}': {e}")
                else:
                    # If it's not a valid expression, add it as is
                    attributes[name] = value

    return attributes


def get_character_info(user_id, guild_id):
    try:
        db_name = f'database/serverid-{guild_id}_database.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Retrieve character information for the specified user_id
        cursor.execute('SELECT clan, oc_url, name FROM personal_info WHERE user_id = ?', (user_id,))
        character_data = cursor.fetchone()

        if character_data:
            clan, oc_url, name = character_data
            return clan, oc_url, name
        else:
            return None

    except sqlite3.Error as err:
        print(f'Error fetching character info: {err}')
        return None

    finally:
        db_name = f'database/serverid-{guild_id}_database.db'
        conn = sqlite3.connect(db_name)
        conn.close()


def format_message(message):
    # Initialize an empty formatted message
    formatted_message = ''

    # Split the message into blocks using '\'
    blocks = message.split('/')

    for block in blocks:
        # Split each block into lines
        lines = block.strip().split('\n')

        for line in lines:
            # Check if the line starts with '+'
            if line.startswith('+'):
                # Format 'Action' messages with italics
                formatted_message += f'*{line[1:]}* '
            # Check if the line starts with '-'
            elif line.startswith('"'):
                # Format 'Speech' messages with bold double quotes
                formatted_message += f'**"** {line[1:]} **"** '
            elif line.startswith('='):
                # Format 'Speech' messages with bold double quotes
                formatted_message += f'**=** {line[1:]} **=** '
            elif '>>' in line:
                # Create a line break if 'p/' is found in the line
                formatted_message += '\n\n'
            else:
                # Add the line as is
                formatted_message += line + ' '

    # Remove the trailing space and return the formatted message
    return formatted_message.strip()


class EmoteFunction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='emote')
    async def emote_command(
            self,
            interactions: Interaction,
            message: str,
            *,
            args: Optional[str] = SlashOption(required=False),
    ):
        # Extract and process the attributes from the input
        attributes = extract_attributes(args)

        if message:
            # Format the message
            formatted_message = format_message(message)

            # Get character information for the author
            character_info = get_character_info(interactions.user.id, interactions.guild.id)

            if character_info:
                clan, oc_url, name = character_info

                # Create an embed with the character's clan and oc_url
                embed = nextcord.Embed(description=formatted_message, color=0x7289DA)
                # Checking if clan is "Na" or null/empty
                if clan == "Na" or "Null":
                    title_value = name
                else:
                    title_value = clan

                embed.title = title_value
                embed.set_thumbnail(url=oc_url)
                embed.set_footer(text=f"Posted by: {interactions.user.name}")

                # Add attribute fields to the embed
                for attribute_name, attribute_value in attributes.items():
                    if attribute_value is not None:
                        embed.add_field(name=attribute_name, value=attribute_value, inline=True)

                # Send the formatted message in an embed
                await interactions.send(embed=embed, allowed_mentions=nextcord.AllowedMentions.none())
            else:
                await interactions.send(
                    "Character information not found. Please create your character using '/create_oc'.")
        else:
            await interactions.send("No emote message found for your input.")


def setup(bot):
    bot.add_cog(EmoteFunction(bot))
