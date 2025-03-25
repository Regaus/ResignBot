import discord
from discord import app_commands
from discord.ext import commands

from utils import general


async def on_command_error(ctx: commands.Context | discord.Interaction, error: commands.CommandError | app_commands.AppCommandError):
    """ Wrapper for text and slash command errors """
    if isinstance(ctx, discord.Interaction):
        ctx: commands.Context = await commands.Context.from_interaction(ctx)

    # Get the message content
    if ctx.interaction is None:
        content = ctx.message.content
    else:
        content = general.slash_command_string(ctx.interaction)
    guild = getattr(ctx.guild, "name", "Private Message") or "Private Server"
    error_message = f"{type(error).__name__}: {str(error)}"

    # If an error occurred with a hybrid slash command, extract the actual exception and handle it accordingly
    if isinstance(error, commands.HybridCommandError):
        error: app_commands.AppCommandError = error.original

    ignore = True
    # Command parsing errors
    if isinstance(error, commands.MissingRequiredArgument):  # A required argument is missing
        helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
        await ctx.send_help(helper, f"A required command argument `{error.param.name}` is missing...")
        message = None  # A message has already been sent
    elif isinstance(error, commands.MissingRequiredAttachment):  # A required argument is missing
        helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
        await ctx.send_help(helper, f"A required attachment `{error.param.name}` is missing...")
        message = None
    elif isinstance(error, commands.TooManyArguments):  # Too many arguments were specified
        helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
        await ctx.send_help(helper, "Too many arguments were specified...")
        message = None

    # Argument parsing errors
    elif isinstance(error, commands.ChannelNotFound):  # The specified Channel was not found
        message = f"The specified channel `{error.argument}` was not found."
    elif isinstance(error, (commands.EmojiNotFound, commands.PartialEmojiConversionFailure)):  # The specified Emoji was not found
        message = f"The specified emoji `{error.argument}` was not found."
    elif isinstance(error, commands.GuildNotFound):  # The specified Guild was not found
        message = f"The specified server `{error.argument}` was not found."
    elif isinstance(error, commands.MemberNotFound):  # The specified Member was not found
        message = f"The specified member `{error.argument}` was not found."
    elif isinstance(error, commands.MessageNotFound):  # The specified Message was not found
        message = f"The specified message `{error.argument}` was not found."
    elif isinstance(error, commands.RoleNotFound):  # The specified Role was not found
        message = f"The specified role `{error.argument}` was not found."
    elif isinstance(error, commands.GuildStickerNotFound):  # The specified Sticker was not found
        message = f"The specified sticker `{error.argument}` was not found."
    elif isinstance(error, commands.ThreadNotFound):  # The specified Thread was not found
        message = f"The specified thread `{error.argument}` was not found."
    elif isinstance(error, commands.UserNotFound):  # The specified User was not found
        message = f"The specified user `{error.argument}` was not found."
    elif isinstance(error, commands.ChannelNotReadable):  # The specified Channel or Thread cannot be read by the bot
        message = f"The bot cannot access the channel `{error.argument}`."
    elif isinstance(error, (commands.ConversionError, commands.UserInputError)):
        # This is a generic condition for other bad argument and parsing/conversion errors
        # We will handle all these errors the same, and just tell the user that an argument is invalid
        helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
        await ctx.send_help(helper, "One of the arguments received an invalid value...")
        message = None
    elif isinstance(error, app_commands.TransformerError):  # Slash command conversion error
        message = f"The given argument `{error.value}` could not be converted to a `{error.type.name}` value."  # type: ignore

    # Errors with permissions and cooldowns
    elif isinstance(error, (commands.NoPrivateMessage, app_commands.NoPrivateMessage)):  # The command cannot be used in DMs
        message = "This command cannot be used in DMs."
    elif isinstance(error, commands.NotOwner):  # The command can only be used by the bot owner
        message = "Only the bot owner can execute this command."
    elif isinstance(error, (commands.MissingRole, app_commands.MissingRole)):  # You need to have a certain role to access this command
        message = f"You need to have the {error.missing_role} role to run this command."
    elif isinstance(error, (commands.MissingAnyRole, app_commands.MissingAnyRole)):  # You need to have at least one of some roles to access this command
        message = f"You need to have the one of the following roles to run this command: {", ".join(error.missing_roles)}"
    elif isinstance(error, commands.BotMissingRole):  # The bot needs to have a certain role to access this command
        message = f"I need to have the {error.missing_role} role to run this command."
    elif isinstance(error, commands.BotMissingAnyRole):  # The bot needs to have at least one of some roles to access this command
        message = f"I need to have the one of the following roles to run this command: {", ".join(error.missing_roles)}"
    elif isinstance(error, (commands.MissingPermissions, app_commands.MissingPermissions)):  # You do not have sufficient permissions to run this command
        message = f"You are missing these required permissions: `{"`, `".join(error.missing_permissions)}`"
    elif isinstance(error, (commands.BotMissingPermissions, app_commands.BotMissingPermissions)):
        message = f"I am missing these required permissions: `{"`, `".join(error.missing_permissions)}`"
    elif isinstance(error, (commands.CommandOnCooldown, app_commands.CommandOnCooldown)):
        message = f"This command is currently on cooldown. Retry in {error.retry_after:.2f} seconds..."
    elif isinstance(error, (commands.CheckFailure, app_commands.CheckFailure)):
        message = "You can't use this command here..."
    elif isinstance(error, (commands.CommandNotFound, commands.DisabledCommand)):
        message = None  # Don't say anything

    # An actual error occurred while running the command
    elif isinstance(error, (commands.CommandInvokeError, app_commands.CommandInvokeError)):
        ignore = False
        error: Exception = error.original
        error_message = f"{type(error).__name__}: {error}"
        message = f"An error occurred:\n{error_message}"
    else:  # Catch-all for any exceptions not mentioned here
        ignore = False
        message = f"An error occurred:\n{error_message}"

    if message:
        await ctx.send(message, ephemeral=True)

    if not ignore:
        error_message = f"{general.iso_time()} > {ctx.bot.name} > {guild} > {ctx.author} ({ctx.author.id}) > {content} > {error_message}"
        general.print_stderr(error_message)
        errors_channel = ctx.bot.get_channel(ctx.bot.config["errors_channel"])
        if errors_channel is not None:
            error_traceback = f"Command: {content[:250]}\nGuild: {guild}\n{general.make_traceback(error)}"
            await errors_channel.send(error_traceback[:2000])  # Make sure the error message fits the limits
