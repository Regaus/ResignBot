import asyncio
import os

import discord

from utils import bot_data, general

print(f"{general.iso_time()} > Signing Resignation Letter...")

# load stuff from bot's config
config = general.load_config()
prefixes = config["prefixes"]
intents = discord.Intents(members=True, messages=True, guilds=True, bans=True, emojis=True, reactions=True, message_content=True)

activity_type = config["activity_type"]
activity_message = config["activity_message"]
match activity_type:
    case "playing":
        activity = discord.Game(name=activity_message)
    case "streaming":
        activity = discord.Streaming(name=activity_message, url=config["streaming_url"])  # Streaming statuses have a URL element
    case "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=activity_message)
    case "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=activity_message)
    case "custom":
        activity = discord.CustomActivity(name=activity_message)
    case "competing":
        activity = discord.Activity(type=discord.ActivityType.competing, name=activity_message)
    case _:
        raise ValueError(f"Unknown activity type {activity_type}")

allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
bot = bot_data.Bot(config=config, command_prefix=prefixes, prefix=prefixes, intents=intents, case_insensitive=True, owner_ids=config["owners"],
                   activity=activity, status=discord.Status.dnd, allowed_mentions=allowed_mentions)

# Load command categories
loop = asyncio.get_event_loop_policy().get_event_loop()
tasks = []
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        tasks.append(loop.create_task(bot.load_extension(f"cogs.{file[:-3]}")))
tasks.append(loop.create_task(bot.start(config["token"])))

try:
    loop.run_until_complete(asyncio.gather(*tasks))
except (KeyboardInterrupt, asyncio.CancelledError, SystemExit):
    loop.close()
