import nextcord
from nextcord.ext import commands
import sqlite3


def insert_character_info(user_id, server_id, name, clan, gender, age, elemental_affinity, oc_url):
    try:
        db_name = f'database/serverid-{server_id}_database.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO personal_info (user_id, name, clan, gender, age, elemental_affinity, oc_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, clan, gender, age, elemental_affinity, oc_url))

        conn.commit()
    except sqlite3.Error as err:
        print(f'Error inserting character info: {err}')
    finally:
        db_name = f'database/serverid-{server_id}_database.db'
        conn = sqlite3.connect(db_name)
        conn.close()


def check_character_existence(user_id, server_id):
    try:
        db_name = f'database/serverid-{server_id}_database.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT user_id FROM personal_info WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None

    except sqlite3.Error as err:
        print(f'Error checking character existence: {err}')
        return False

    finally:
        db_name = f'database/serverid-{server_id}_database.db'
        conn = sqlite3.connect(db_name)
        conn.close()


class NarutoCharacterEditLogic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='create_oc', description='Create your Naruto character.')
    async def create_oc_command(self, interactions: nextcord.Interaction):
        user_id = interactions.user.id
        server_id = interactions.guild.id

        # Check if user already has character data
        if check_character_existence(user_id, server_id):
            await interactions.send('Contact a Lore to reset your character data.')
            return

        # Ask for character information
        name = await self.get_user_input(interactions, 'First Name')
        clan = await self.get_user_input(interactions, 'Clan')
        gender = await self.get_user_input(interactions, 'Gender')
        age = await self.get_age_input(interactions)
        elemental_affinity = await self.get_user_input(interactions, 'Elemental Affinity')
        oc_url = await self.get_oc_url_input(interactions)

        # Insert character information into the database
        insert_character_info(user_id, server_id, name, clan, gender, age, elemental_affinity, oc_url)
        # Insert default stats for the user
        self.insert_default_stats(user_id, server_id)
        await interactions.send('Character creation complete!', ephemeral=True)

    async def get_user_input(self, interactions, prompt):
        for _ in range(3):  # Try 3 times
            input_message = await interactions.send(prompt, ephemeral=True)
            response = await self.bot.wait_for('message', check=lambda m: m.author == interactions.user, timeout=60)

            # Adjust the input
            user_input = response.content.capitalize()

            # Confirm the input
            confirmation_message = await interactions.send(f'You entered: "{user_input}". Is this correct? (yes/no)',
                                                           ephemeral=True)
            confirmation = await self.bot.wait_for('message', check=lambda m: m.author == interactions.user, timeout=60)

            if confirmation.content.lower() == 'yes':
                # Delete both the input and confirmation messages
                await input_message.delete()
                await confirmation_message.delete()
                return user_input
            else:
                await interactions.send('Please resubmit your input.', ephemeral=True)

        return None

    async def get_age_input(self, interactions):
        for _ in range(3):  # Try 3 times
            await interactions.send('Age (must be an integer):', ephemeral=True)
            response = await self.bot.wait_for('message', check=lambda m: m.author == interactions.user, timeout=60)

            # Attempt to convert the input to an integer
            try:
                age = int(response.content)
            except ValueError:
                await interactions.send('Invalid age format. Please enter a valid integer.', ephemeral=True)
                continue

            # Confirm the input
            await interactions.send(f'You entered: "{age}". Is this correct? (yes/no)', ephemeral=True)
            confirmation = await self.bot.wait_for('message', check=lambda m: m.author == interactions.user, timeout=60)

            if confirmation.content.lower() == 'yes':
                return age
            else:
                await interactions.send('Please resubmit your input.', ephemeral=True)

        return None

    async def get_oc_url_input(self, interactions):
        for _ in range(3):  # Try 3 times
            await interactions.send('URL to your OC\'s appearance:', ephemeral=True)
            response = await self.bot.wait_for('message', check=lambda m: m.author == interactions.user, timeout=60)

            # Validate the URL format (you can add more checks here)
            valid_extensions = ['.jpeg', '.jpg', '.png', '.gif', '.webp']
            if any(response.content.lower().endswith(ext) for ext in valid_extensions):
                oc_url = response.content
            else:
                await interactions.send('Invalid URL format. Please enter a valid image URL.', ephemeral=True)
                continue

            # Confirm the input
            await interactions.send(f'You entered: "{oc_url}". Is this correct? (yes/no)', ephemeral=True)
            confirmation = await self.bot.wait_for('message', check=lambda m: m.author == interactions.user, timeout=60)

            if confirmation.content.lower() == 'yes':
                return oc_url
            else:
                await interactions.send('Please resubmit your input.')

        return None

    def insert_default_stats(self, user_id, server_id):
        try:
            db_name = f'database/serverid-{server_id}_database.db'
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            user_id = nextcord.Interaction.user.id

            cursor.execute('''
                INSERT INTO statistical_info (
                    user_id, taijutsu, endurance, agility, perception, 
                    chakra_potency, chakra_reserves, stamina, current_stamina, 
                    current_chakra_reserves, senjutsu_potency, current_senjutsu_reserves, 
                    available_points, total
                )
                VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            ''', (user_id,))

            conn.commit()
        except sqlite3.Error as err:
            print(f'Error inserting default stats: {err}')
        finally:
            db_name = f'database/serverid-{server_id}_database.db'
            conn = sqlite3.connect(db_name)
            conn.close()


def setup(bot):
    bot.add_cog(NarutoCharacterEditLogic(bot))
