import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import sqlite3


class NarutoBotJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = None  # SQLite connection

    @nextcord.slash_command(name='startup')
    async def cybrus_startup(self, interactions: Interaction):
        """Initialize the bot after joining a server."""
        await self.on_bot_join(interactions.guild)

        await interactions.send("Initialization complete!")

    @commands.Cog.listener()
    async def on_bot_join(self, guild):
        user_id = self.bot.user.id
        # Connect to the SQLite database
        self.connect_to_database(user_id, guild)
        # Create tables for personal, statistical, jutsu, and promotional data
        self.create_personal_info_table()
        self.create_statistical_info_table()
        self.create_jutsu_catalogue_table()
        self.create_promotional_rules_table()

        print(f'Bot joined guild: {guild.name}')

    def connect_to_database(self, user_id, guild):

        try:
            db_name = f'database/serverid-{guild.id}_database.db'
            self.db_connection = sqlite3.connect(db_name)
            print(f'Connected to SQLite database: {db_name}')
        except sqlite3.Error as err:
            print(f'Error connecting to database: {err}')

    def create_personal_info_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_info (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                rank TEXT,
                gender TEXT,
                clan TEXT,
                elemental_affinity TEXT,
                oc_url TEXT
            )
        ''')
        cursor.close()

    def create_statistical_info_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistical_info (
                user_id INTEGER PRIMARY KEY,
                taijutsu INTEGER,
                endurance INTEGER,
                agility INTEGER,
                perception INTEGER,
                chakra_potency INTEGER,
                chakra_reserves INTEGER,
                stamina INTEGER,
                current_stamina INTEGER,
                current_chakra_reserves INTEGER,
                senjutsu_potency INTEGER,
                current_senjutsu_reserves INTEGER,
                available_points INTEGER,
                total INTEGER
            )
        ''')
        cursor.close()

    def create_jutsu_catalogue_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jutsu_catalogue (
                jutsu_id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT
            )
        ''')
        cursor.close()

    def create_promotional_rules_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promotional_rules (
                rule_id INTEGER PRIMARY KEY,
                rule_text TEXT
            )
        ''')
        cursor.close()


def setup(bot):
    bot.add_cog(NarutoBotJoin(bot))
