import random

import discord
from discord import app_commands
from discord.ext import commands

from utils import bot_data, emotes, general


class Fun(commands.Cog):
    """ Just some funny commands """

    def __init__(self, bot: bot_data.Bot):
        self.bot = bot
        self.last_deleted_messages: dict[int, discord.Message] = {}

    @commands.hybrid_command(name="resign")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.describe(member="The member who you want to resign")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def resign(self, ctx: commands.Context, member: discord.Member = None):
        """ RESIGN! """
        if member is None:
            return await ctx.send(emotes.RESIGN, ephemeral=True)
        return await ctx.send(f"{member.mention} {emotes.RESIGN}", ephemeral=False)

    @commands.hybrid_command(name="shrug")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    async def shrug(self, ctx: commands.Context):
        """ ¯\\_(ツ)_/¯ """
        return await ctx.send(f"¯\\\\_(ツ)\\_/¯", ephemeral=True)

    @commands.hybrid_command(name="vibe")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.describe(member="The member whose vibe to check")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def vibe_check(self, ctx: commands.Context, member: discord.Member = None):
        """ Vibe-check someone """
        if member is None:
            member = ctx.author
        if random.random() < 0.5:
            return await ctx.send(f"{member.global_name} has **failed** the test because they are a vibe coder.")
        return await ctx.send(f"{member.global_name} has **passed** the test.")

    @commands.hybrid_command(name="coin")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def coin_flip(self, ctx: commands.Context):
        """ Flip a coin """
        return await ctx.send(f"The coin lands on **{random.choice(("Heads", "Tails"))}**.")

    @commands.hybrid_command(name="snipe")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @commands.guild_only()
    @app_commands.allowed_installs(guilds=True, users=False)  # Cannot be used in user installs
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def snipe(self, ctx: commands.Context):
        """ Catch the last deleted message in this channel """
        message = self.last_deleted_messages.get(ctx.channel.id)
        if message is None:
            return await ctx.send("There is nothing to snipe in this channel...", ephemeral=True)
        embed = discord.Embed(colour=general.random_colour())
        if message.message_snapshots:
            embed.title = "Forwarded Message Sniped"
            snapshot = message.message_snapshots[0]
            embed.description = snapshot.content
        else:
            embed.title = "Message Sniped"
            embed.description = message.system_content
        embed.set_author(name=message.author.global_name, icon_url=message.author.display_avatar)
        embed.timestamp = message.created_at
        return await ctx.send(embed=embed, ephemeral=False)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """ Triggered when a message is deleted """
        self.last_deleted_messages[message.channel.id] = message


async def setup(bot: bot_data.Bot):
    await bot.add_cog(Fun(bot))
