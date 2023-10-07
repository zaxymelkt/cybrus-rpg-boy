import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import sqlite3


class StatUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='stat', description='Update your stats.')
    async def stat(self, interaction: nextcord.Interaction, action: str):
        if action == "update":
            db = sqlite3.connect(f"database/serverid-{guild_id}_database.db")
            cursor = db.cursor()

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS reward_logs (
                                staff_id INTEGER,
                                participants TEXT,
                                point_rewards INTEGER,
                                event_link TEXT
                            )
                            """)

            db.commit()
            db.close()
            await self.show_stat_menu(interaction)

    async def show_stat_menu(self, interaction):
        # Connect to database
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        # Fetch user's data
        cursor.execute(
            "SELECT available_points, agility, taijutsu, endurance, perception, chakra_potency FROM statistical_info "
            "WHERE user_id = ?",
            (interaction.user.id,))
        data = cursor.fetchone()

        if not data:
            await interaction.send("You're not registered!")
            return

        available_points, agility, taijutsu, endurance, perception, chakra_potency = data

        # Create embedded menu
        embed = nextcord.Embed(title="Update Stats", description=f"Available Points: {available_points}")
        embed.add_field(name="Agility", value=f":one: {agility}", inline=False)
        embed.add_field(name="Taijutsu", value=f":two: {taijutsu}", inline=False)
        embed.add_field(name="Endurance", value=f":three: {endurance}", inline=False)
        embed.add_field(name="Perception", value=f":four: {perception}", inline=False)
        embed.add_field(name="Potency", value=f":five: {chakra_potency}", inline=False)

        await interaction.send(embed=embed, view=StatView(self.bot), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if "finish" in message.content.lower():
            # Finish the update, maybe save to database or some other logic.
            pass

    @nextcord.slash_command(name='admin', description='Update stats for users.')
    async def stat_add(self, interaction, action: str, user_id: str, stat_point_total: int, event_link: str):
        if action == "reward":
            roles = [role.name for role in interaction.user.roles]
            authorized_roles = ["Lore Write", "Lore Manager", "Truck-Kun"]
            try:
                user_id = int(user_id)
            except ValueError:
                await interaction.send("Provided user ID is not valid.", ephemeral=True)
                return

            if not any(role in roles for role in authorized_roles):
                await interaction.send("You don't have permission to use this command!", ephemeral=True)
                return

            # Connect to database
            db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
            cursor = db.cursor()

            # Update the user's available_points
            cursor.execute("SELECT available_points FROM statistical_info WHERE user_id = ?", (user_id,))
            current_points = cursor.fetchone()
            if not current_points:
                await interaction.send(f"{user_id} is not registered!", ephemeral=True)
                return

            new_total = current_points[0] + stat_point_total
            # Here's the change. Instead of inserting, we update the existing row.
            cursor.execute("UPDATE statistical_info SET available_points = ? WHERE user_id = ?",
                           (new_total, user_id))

            # Log the command usage in reward_logs table
            cursor.execute(
                "INSERT INTO reward_logs (staff_id, participants, point_rewards, event_link) VALUES (?, ?, ?, ?)",
                (interaction.user.id, user_id, stat_point_total, event_link))

            # Commit and close the database
            db.commit()
            db.close()

            await interaction.send(f"Updated {user_id}'s points by {stat_point_total}. New total: {new_total}",
                                   ephemeral=True)


class StatUpdateView(nextcord.ui.View):
    def __init__(self, interaction, attribute_name, cursor, user_id):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.attribute_name = attribute_name
        self.cursor = cursor
        self.user_id = user_id

    async def update_stat(self, points_to_add, guild):
        # Move the database connection inside the method, so a new connection is created for each operation
        db = sqlite3.connect(f"database/serverid-{guild.id}_database.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT available_points, {self.attribute_name} FROM statistical_info WHERE user_id = ?",
                       (self.user_id,))
        available_points, current_stat = cursor.fetchone()

        if points_to_add <= available_points:
            new_total = current_stat + points_to_add
            cursor.execute(
                f"UPDATE statistical_info SET {self.attribute_name} = ?, available_points = ? WHERE user_id = ?",
                (new_total, available_points - points_to_add, self.user_id))
            db.commit()
            await self.interaction.send(f"You added {points_to_add} points to {self.attribute_name}."
                                        f" Your now have {available_points} points left.", ephemeral=True)
        else:
            await self.interaction.send("You don't have enough points!", ephemeral=True)

        db.close()

    @nextcord.ui.button(label='+1')
    async def plus_one(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_stat(1, guild=interaction.guild)

    @nextcord.ui.button(label='+2')
    async def plus_two(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_stat(2, guild=interaction.guild)

    @nextcord.ui.button(label='+3')
    async def plus_three(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_stat(3, guild=interaction.guild)

    @nextcord.ui.button(label='+4')
    async def plus_four(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_stat(4, guild=interaction.guild)

    @nextcord.ui.button(label='+5')
    async def plus_five(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_stat(5, guild=interaction.guild)

    @nextcord.ui.button(label='+10')
    async def plus_ten(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.update_stat(10, guild=interaction.guild)


class StatView(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # make the view persistent
        self.bot = bot

    @nextcord.ui.button(label="Agility", style=nextcord.ButtonStyle.primary)
    async def agility_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # Connect to database
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        # Fetch user's data
        cursor.execute(f"SELECT available_points, agility FROM statistical_info WHERE user_id = ?",
                       (interaction.user.id,))
        data = cursor.fetchone()

        if not data:
            await interaction.send("You're not registered!", ephemeral=True)
            return

        available_points, agility = data

        # Create an embed with instructions
        embed = nextcord.Embed(title=f"Update Agility",
                               description=f"You have {available_points} available points. Click on the buttons"
                                           f" to add points to Agility.")

        # Send the embed with the view containing the buttons
        view = StatUpdateView(interaction, 'agility', cursor, interaction.user.id)
        await interaction.send(embed=embed, view=view, ephemeral=True)

        # The database commit and close operations are now handled by the individual button click methods.
        db.commit()
        db.close()

    @nextcord.ui.button(label="Taijutsu", style=nextcord.ButtonStyle.primary)
    async def taijutsu_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT available_points, taijutsu FROM statistical_info WHERE user_id = ?",
                       (interaction.user.id,))
        data = cursor.fetchone()

        if not data:
            await interaction.send("You're not registered!", ephemeral=True)
            return

        available_points, taijutsu = data

        embed = nextcord.Embed(title=f"Update Taijutsu",
                               description=f"You have {available_points} available points. Click on the buttons"
                                           f" to add points to Taijutsu.")
        view = StatUpdateView(interaction, 'taijutsu', cursor, interaction.user.id)
        await interaction.send(embed=embed, view=view, ephemeral=True)
        db.commit()
        db.close()

    @nextcord.ui.button(label="Endurance", style=nextcord.ButtonStyle.primary)
    async def endurance_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT available_points, endurance FROM statistical_info WHERE user_id = ?",
                       (interaction.user.id,))
        data = cursor.fetchone()

        if not data:
            await interaction.send("You're not registered!", ephemeral=True)
            return

        available_points, endurance = data

        embed = nextcord.Embed(title=f"Update Endurance",
                               description=f"You have {available_points} available points. Click on the buttons"
                                           f" to add points to Endurance.")
        view = StatUpdateView(interaction, 'endurance', cursor, interaction.user.id)
        await interaction.send(embed=embed, view=view, ephemeral=True)
        db.commit()
        db.close()

    @nextcord.ui.button(label="Perception", style=nextcord.ButtonStyle.primary)
    async def perception_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT available_points, perception FROM statistical_info WHERE user_id = ?",
                       (interaction.user.id,))
        data = cursor.fetchone()

        if not data:
            await interaction.send("You're not registered!", ephemeral=True)
            return

        available_points, perception = data

        embed = nextcord.Embed(title=f"Update Perception",
                               description=f"You have {available_points} available points. Click on the buttons"
                                           f" to add points to Perception.")
        view = StatUpdateView(interaction, 'perception', cursor, interaction.user.id)
        await interaction.send(embed=embed, view=view, ephemeral=True)
        db.commit()
        db.close()

    @nextcord.ui.button(label="Potency", style=nextcord.ButtonStyle.primary)
    async def potency_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        db = sqlite3.connect(f"database/serverid-{interaction.guild.id}_database.db")
        cursor = db.cursor()

        cursor.execute(f"SELECT available_points, chakra_potency FROM statistical_info WHERE user_id = ?",
                       (interaction.user.id,))
        data = cursor.fetchone()

        if not data:
            await interaction.send("You're not registered!", ephemeral=True)
            return

        available_points, chakra_potency = data

        embed = nextcord.Embed(title=f"Update Potency",
                               description=f"You have {available_points} available points. Click on the buttons"
                                           f" to add points to Potency.")
        view = StatUpdateView(interaction, 'chakra_potency', cursor, interaction.user.id)
        await interaction.send(embed=embed, view=view, ephemeral=True)
        db.commit()
        db.close()


def setup(bot):
    bot.add_cog(StatUpdate(bot))
