import json
import random
import sys
import traceback
from datetime import datetime

import discord


def load_config():
    """ Load the config file """
    return json.load(open("config.json", "r", encoding="utf-8"))


def make_traceback(error: BaseException) -> str:
    """ Make the error traceback string """
    if hasattr(error, "__traceback__"):
        error_traceback = "".join(traceback.format_tb(error.__traceback__))
    else:
        error_traceback = "Traceback not available"
    error_message = f"{type(error).__name__}: {error}"
    return f"```py\n{error_traceback}\n{error_message}\n```"


def print_stderr(*values):
    """ Print to standard error """
    return print(*values, file=sys.stderr)


def random_colour() -> int:
    """ Get a random colour """
    return random.randint(0, 0xffffff)


def slash_command_string(interaction: discord.Interaction) -> str:
    """ Get the slash command string from an interaction """
    command = "/" + interaction.command.qualified_name
    arguments: list[str] = []
    for key, value in interaction.namespace:  # type: ignore
        if value is not None:
            arguments.append(f"{key}={value}")
    return f"{command} {" ".join(arguments)}"


def now() -> datetime:
    """ Get the current time """
    return datetime.now()


def iso_time(when: datetime = None) -> str:
    """ Show a given time in ISO format """
    if when is None:
        when = now()
    return when.isoformat(sep=" ", timespec="seconds")


def human_time(when: datetime = None) -> str:
    """ Show a given time in a nicer-looking format """
    if when is None:
        when = now()
    return when.strftime("%d %B %Y, %H:%M:%S")


def parse_time(when: str) -> datetime:
    """ Parse the provided time from a string """
    return datetime.fromisoformat(when)
