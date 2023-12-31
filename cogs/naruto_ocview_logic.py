import sqlite3
import nextcord
from nextcord.ext import commands


class NarutoOCViewLogic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("NarutoOcViewLogic cog is ready!")

    # Define the /oc command to display the character sheet
    @nextcord.slash_command(name='viewoc', description='View your character sheet.')
    async def view_character_sheet(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        # Connect to the database
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        # Fetch data from 'personal_info' table
        cursor.execute(
            "SELECT clan, name, age, gender, elemental_affinity, oc_url FROM personal_info WHERE user_id = ?",
            (user_id,)
        )
        personal_data = cursor.fetchone()

        if not personal_data:
            await interaction.send("You don't have a character sheet!", ephemeral=True)
            db.close()
            return

        clan, name, age, gender, elemental_affinity, oc_url = personal_data

        # Fetch data from 'statistical_info' table
        cursor.execute(
            "SELECT agility, taijutsu, endurance, perception, chakra_potency, available_points, total "
            "FROM statistical_info WHERE user_id = ?",
            (user_id,)
        )
        stat_data = cursor.fetchone()

        if not stat_data:
            await interaction.send("Your stats are missing!", ephemeral=True)
            db.close()
            return

        agility, taijutsu, endurance, perception, chakra_potency, available_points, total_points = stat_data

        # Create an embedded message to display the character sheet
        embed = nextcord.Embed(color=0x00ff00)
        embed.set_image(url=oc_url)
        embed.description = description = (
            f"Name{'.' * (27 - len(name))}{name}\n"
            f"Clan{'.' * (30 - len(clan))}{clan}\n"
            f"Age{'.' * (30 - len(str(age)))}{age}\n"
            f"Gender{'.' * (26 - len(gender))}{gender}\n"
            f"Affinity{'.' * (26 - len(elemental_affinity))}{elemental_affinity}\n"
        )
        embed.add_field(name="Statistical Info",
                        value=f"Agility: {agility}\nTaijutsu: {taijutsu}\nEndurance: {endurance}\nPerception: "
                              f"{perception}\nPotency: {chakra_potency}\nSaved Points: {available_points}\n"
                              f"Point Total: {total_points}", inline=False)

        if clan.lower() in ["null", "na"]:
            embed.title = f"{name} — Original Character Sheet"
        else:
            embed.title = f"{clan}, {name} — Original Character Sheet"

        # Send the embedded message as an ephemeral message
        await interaction.send(embed=embed, ephemeral=True)

        # Close the database connection
        db.close()


def setup(bot):
    bot.add_cog(NarutoOCViewLogic(bot))