import time

import discord
from discord import app_commands
from discord.ext import commands

from utils import bot_data, general


class Information(commands.Cog):
    """ Information about the bot and the stuff within """

    def __init__(self, bot: bot_data.Bot):
        self.bot = bot

    @commands.hybrid_command(name="stats")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def stats(self, ctx: commands.Context):
        """ Show information about the bot """
        await ctx.defer(ephemeral=True)
        version = self.bot.config["version"]
        last_update = general.iso_time(general.parse_time(self.bot.config["last_update"]))

        embed = discord.Embed(colour=general.random_colour())
        embed.title = f"Stats about {self.bot.name} | v{version}"
        embed.set_thumbnail(url=str(self.bot.user.display_avatar.replace(size=1024, static_format="png")))

        embed.add_field(name="Developer", value="\n".join(self.bot.get_user(uid).global_name for uid in self.bot.config["owners"]), inline=True)
        uptime = general.now() - self.bot.uptime
        embed.add_field(name="Uptime", value=str(uptime), inline=True)
        embed.add_field(name="Commands", value=str(len(self.bot.commands)), inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Last Update", value=last_update, inline=False)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(name="server", aliases=["guild"])
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @commands.guild_only()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def server(self, ctx: commands.Context):
        """ Show information about this server """
        await ctx.defer(ephemeral=True)
        embed = discord.Embed(colour=general.random_colour())
        embed.title = f"Information about server {ctx.guild.name}"
        embed.set_thumbnail(url=str(ctx.guild.icon.replace(size=1024, static_format="png")))

        embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Server Owner", value=f"{ctx.guild.owner.mention} ({ctx.guild.owner.name})", inline=True)
        embed.add_field(name="Member Count", value=str(ctx.guild.member_count), inline=True)
        embed.add_field(name="Bot Count", value=str(sum(1 for member in ctx.guild.members if member.bot)), inline=True)
        embed.add_field(name="Roles", value=str(len(ctx.guild.roles)), inline=True)
        embed.add_field(name="Channels", value=str(len(ctx.guild.channels)), inline=True)
        embed.add_field(name="Emotes", value=str(len(ctx.guild.emojis)), inline=True)
        embed.add_field(name="Stickers", value=str(len(ctx.guild.stickers)), inline=True)
        embed.add_field(name="Soundboard Sounds", value=str(len(ctx.guild.soundboard_sounds)), inline=True)
        embed.add_field(name="Server Creation", value=general.human_time(ctx.guild.created_at), inline=False)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(name="user")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.describe(user="The user whose information to show")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def user(self, ctx: commands.Context, user: discord.User = None):
        """ Show information about a user """
        await ctx.defer(ephemeral=True)
        if user is None:
            user = ctx.author
        if ctx.guild is not None:
            member: discord.Member | None = ctx.guild.get_member(user.id)  # Try to find the user in this guild
        else:
            member = None

        embed = discord.Embed(colour=general.random_colour())
        embed.title = f"Information about user {user.global_name}"
        embed.set_thumbnail(url=str(user.display_avatar.replace(size=1024, static_format="png")))

        embed.add_field(name="Username", value=user.name, inline=True)
        if user.global_name:
            embed.add_field(name="Global Name", value=user.global_name, inline=True)
        if member is not None:
            embed.add_field(name="Nickname", value=member.nick, inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Is a Bot", value="Yes" if user.bot else "No", inline=True)

        embed.add_field(name="Account Creation", value=general.human_time(user.created_at), inline=False)
        if member is not None:
            embed.add_field(name="Server Member Since", value=general.human_time(member.joined_at), inline=False)
            if not member.roles:
                roles = "None"
            else:
                roles = "\n".join(role.mention for role in member.roles[::-1] if not role.is_default())  # List all the roles that the member has
            embed.add_field(name="Roles", value=roles, inline=False)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(name="time")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def time(self, ctx: commands.Context):
        """ Get the current time """
        await ctx.defer(ephemeral=True)
        return await ctx.send(f"It is currently **{general.human_time()}**.")

    @commands.hybrid_command(name="ping")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ping(self, ctx: commands.Context):
        """ Check how slow Discord API is today """
        await ctx.defer(ephemeral=True)
        socket = int(self.bot.latency * 1000)
        time1 = time.time()
        msg = await ctx.send(f"Message Send: unknown\nMessage Edit: unknown\nWS Latency: {socket:,}ms")
        send = int((time.time() - time1) * 1000)
        time2 = time.time()
        await msg.edit(content=f"Message Send: {send:,}ms\nMessage Edit: unknown\nWS Latency: {socket:,}ms")
        edit = int((time.time() - time2) * 1000)
        await msg.edit(content=f"Message Send: {send:,}ms\nMessage Edit: {edit:,}ms\nWS Latency: {socket:,}ms")

    @commands.hybrid_command(name="invite")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def invite(self, ctx: commands.Context):
        """ Invite this bot to another server """
        await ctx.defer(ephemeral=True)
        perms = 67488832
        link = discord.utils.oauth_url(str(self.bot.user.id), permissions=discord.Permissions(perms), scopes=['bot', 'applications.commands'])
        return await ctx.send(f"Use [this link]({link}) to invite me to another server.")


async def setup(bot: bot_data.Bot):
    await bot.add_cog(Information(bot))
