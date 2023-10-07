import nextcord
from nextcord import Interaction
from nextcord.ext import commands


class BotManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='reload')
    async def reload_cog(self, interactions: Interaction, cog_name: str):
        if interactions.user.guild_permissions.administrator:
            try:
                # Unload the specified cog
                self.bot.unload_extension(cog_name)

                # Load the specified cog
                self.bot.load_extension(cog_name)

                await interactions.send(f"Cog '{cog_name}' reloaded successfully.", delete_after=5)
            except commands.ExtensionNotLoaded:
                await interactions.send(f"Cog '{cog_name}' is not loaded.", delete_after=5)
            except commands.ExtensionNotFound:
                await interactions.send(f"Cog '{cog_name}' does not exist.", delete_after=5)
            except Exception as e:
                await interactions.send(f"An error occurred while reloading '{cog_name}': {e}", delete_after=5)


def setup(bot):
    bot.add_cog(BotManagementCog(bot))
