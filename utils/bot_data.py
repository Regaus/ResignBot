from datetime import datetime
from typing import override

import discord
from discord import app_commands
from discord.ext import commands

from utils import errors


class Bot(commands.Bot):
    def __init__(self, config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config: dict = config  # Config stored inside the bot
        self.name: str = config["name"]
        self.uptime: datetime | None = None

    @override
    async def on_message(self, message: discord.Message):
        # Ignore commands from before the bot is done loading, as well as messages from bots
        if not self.is_ready() or message.author.bot:
            return
        await self.process_commands(message)

    @override
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """ Handle command errors """
        return await errors.on_command_error(ctx, error)

    @staticmethod
    async def on_slash_command_error(ctx: discord.Interaction, error: app_commands.AppCommandError):
        """ Handle slash command errors """
        return await errors.on_command_error(ctx, error)
