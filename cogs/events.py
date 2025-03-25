import discord
from discord.ext import commands

from utils import bot_data, general


class Events(commands.Cog):
    def __init__(self, bot: bot_data.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        """ Triggered when a command successfully completes """
        guild = getattr(ctx.guild, "name", "Private Message") or "Private Server"
        content = ctx.message.clean_content if ctx.interaction is None else general.slash_command_string(ctx.interaction)
        print(f"{general.iso_time()} > {self.bot.name} > {guild} > {ctx.author} ({ctx.author.id}) > {content}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """ Triggered when the bot joins a new guild """
        print(f"{general.iso_time()} > {self.bot.name} > Joined {guild.name} ({guild.id})")

        if self.bot.config["join_message"]:
            # Find a text channel where we can send the "join message" and send it there
            try:
                channel = sorted([c for c in guild.channels if c.permissions_for(guild.me).send_messages and isinstance(c, discord.TextChannel)],
                                 key=lambda x: x.position)[0]
            except IndexError:
                pass
            else:
                await channel.send(self.bot.config["join_message"])

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """ Triggered when the bot leaves a guild """
        print(f"{general.iso_time()} > {self.bot.name} > Left {guild.name} ({guild.id})")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """ Triggered when a member joins a guild """
        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """ Triggered when a member leaves a guild """
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        """ Triggered when the bot has connected to Discord """
        if self.bot.uptime is None:
            self.bot.uptime = general.now()
        print(f"{general.iso_time()} > {self.bot.name} > Connected to Discord as {self.bot.user} - {len(self.bot.guilds)} guilds, {len(self.bot.users)} users")


async def setup(bot: bot_data.Bot):
    await bot.add_cog(Events(bot))
