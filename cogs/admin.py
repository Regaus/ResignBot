import sys
import time

from discord.ext import commands

from utils import bot_data, general


# These commands are for managing the bot, so they are owner-only text commands
class Admin(commands.Cog):
    """ Commands for managing the bot """

    def __init__(self, bot: bot_data.Bot):
        self.bot = bot

    @commands.command(name="error")
    @commands.is_owner()
    async def raise_error(self, ctx: commands.Context):
        """ Simulate an unhandled error """
        raise RuntimeError("This is an example error")

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx: commands.Context, cog_name: str):
        """ Reload an extension """
        await self.bot.reload_extension(f"cogs.{cog_name}")
        return await ctx.send(f"Successfully reloaded extension `cogs/{cog_name}.py`.")

    @commands.command(name="config")
    @commands.is_owner()
    async def update_config(self, ctx: commands.Context):
        """ Reload the config file """
        self.bot.config = general.load_config()
        return await ctx.send(f"Successfully reloaded `config.json`.")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context):
        """ Shut down the bot """
        await ctx.send("Shutting down...")
        print(f"{general.iso_time()} > {self.bot.name} > Shutting down...")
        time.sleep(1)
        sys.stderr.close()
        sys.exit(0)

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_slash_commands(self, ctx: commands.Context, action: str = ""):
        """ Synchronise slash commands

         (Empty) -> sync global slash commands
         local -> sync local slash commands for the current server
         global -> copy global slash commands to this server
         clear -> clear guild-specific slash commands from this server """
        # Based on https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html
        async with ctx.typing():
            if not action:
                result = await self.bot.tree.sync()
                return await ctx.send(f"Synchronised {len(result)} slash commands")
            if action == "local":
                result = await self.bot.tree.sync(guild=ctx.guild)
                return await ctx.send(f"Synchronised {len(result)} local slash commands in this server")
            if action == "global":
                self.bot.tree.copy_global_to(guild=ctx.guild)
                result = await self.bot.tree.sync(guild=ctx.guild)
                return await ctx.send(f"Copied {len(result)} global slash commands to this server")
            if action == "clear":
                self.bot.tree.clear_commands(guild=ctx.guild)
                result = await self.bot.tree.sync(guild=ctx.guild)
                return await ctx.send(f"Cleared {len(result)} guild-specific slash commands from this server")


async def setup(bot: bot_data.Bot):
    await bot.add_cog(Admin(bot))
