import random
from io import BytesIO

import discord
from PIL import Image, UnidentifiedImageError
from discord import app_commands
from discord.ext import commands

from utils import bot_data, images, general


FILTERS: list[str] = ["blur", "deepfry", "flip", "grayscale", "invert", "jpegify", "mirror", "pixelate", "rank", "sepia", "spread", "wide"]
FILTER_CHOICES: list[app_commands.Choice[str]] = [
    # app_commands.Choice(name="List available filters", value="list"),
    app_commands.Choice(name="Random filter", value="random"),
    app_commands.Choice(name="Blur", value="blur"),
    app_commands.Choice(name="Deepfry", value="deepfry"),
    app_commands.Choice(name="Flip vertically", value="flip"),
    app_commands.Choice(name="Black and white", value="grayscale"),
    app_commands.Choice(name="Invert colours", value="invert"),
    app_commands.Choice(name="Jpegify", value="jpegify"),
    app_commands.Choice(name="Mirror (Flip horizontally)", value="mirror"),
    app_commands.Choice(name="Pixelate", value="pixelate"),
    app_commands.Choice(name="Rank filter", value="rank"),
    app_commands.Choice(name="Sepia", value="sepia"),
    app_commands.Choice(name="Spread pixels", value="spread"),
    app_commands.Choice(name="Wide", value="wide"),
]


class Images(commands.Cog):
    """ Commands about image manipulation """

    def __init__(self, bot: bot_data.Bot):
        self.bot = bot

    @commands.hybrid_command(name="colour")
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @app_commands.describe(colour="The hex code of the colour")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def colour(self, ctx: commands.Context, colour: str = None):
        """ Information about a colour """
        await ctx.defer(ephemeral=True)
        if not colour:
            int_6 = general.random_colour()
            hex_6 = hex(int_6)[2:]  # Remove the 0x prefix
            rgb_255 = images.colour_int_to_tuple(int_6)
        else:
            try:
                hex_6 = colour
                int_6 = images.colour_hex_to_int(colour)
                rgb_255 = images.colour_int_to_tuple(int_6)
            except images.InvalidLength as e:
                return await ctx.send(f"The colour value must be 6 characters long. Received `{e.value}`, which is {e.length} characters.", ephemeral=True)
            except images.InvalidColour as e:
                return await ctx.send(f"The colour value is invalid: {e.error}\nThe colour must be a hexadecimal RGB value.", ephemeral=True)

        embed = discord.Embed(colour=int_6)
        rgb_1 = tuple(round(value / 255, 4) for value in rgb_255)
        red, green, blue = rgb_255
        brightness = images.calculate_brightness(red, green, blue)
        embed.add_field(name="Hexadecimal", value="#" + hex_6, inline=False)
        embed.add_field(name="Integer", value=str(int_6), inline=False)
        embed.add_field(name="RGB tuple (0-255)", value=str(rgb_255), inline=False)
        embed.add_field(name="RGB tuple (0-1)", value=str(rgb_1), inline=False)
        embed.add_field(name="Brightness", value=f"{brightness:.4f}", inline=False)
        embed.add_field(name="Text Colour", value="#000000" if brightness >= 128 else "#ffffff", inline=False)

        image = Image.new(mode="RGBA", size=(512, 512), color=rgb_255)
        bio = images.save_to_bio(image)
        embed.set_image(url="attachment://colour.png")
        return await ctx.send(embed=embed, file=discord.File(bio, "colour.png"))

    @staticmethod
    async def _filter_command(ctx: commands.Context, asset: discord.Asset | discord.Attachment, filter_name: str):
        """ Wrapper for the two filter subcommands """
        filter_name = filter_name.lower()
        if filter_name == "random":
            filter_name = random.choice(FILTERS)
        async with ctx.typing(ephemeral=False):  # Defers the interaction
            bio = BytesIO()
            await asset.save(bio)
            try:
                image = Image.open(bio)
            except UnidentifiedImageError:
                return await ctx.send("The provided image does not seem to be valid...")
        output: Image | list[Image] = getattr(images, filter_name)(image)
        output_bio = images.save_to_bio(output)
        file_format = "gif" if isinstance(output, list) else "png"
        return await ctx.send(file=discord.File(output_bio, filename=f"{filter_name}.{file_format}"))

    @commands.hybrid_group(name="filter", case_insensitive=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def filter(self, ctx: commands.Context):
        """ Apply a filter on an image """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @filter.command(name="list")
    async def filter_list(self, ctx: commands.Context):
        """ List available filters """
        return await ctx.send(f"The following filters are currently available:\n`{"`, `".join(FILTERS)}`", ephemeral=True)

    @filter.command(name="user")
    @app_commands.describe(user="The user whose avatar to apply the filter on", filter_name="The name of the filter to apply")
    @app_commands.choices(filter_name=FILTER_CHOICES)
    async def filter_user(self, ctx: commands.Context, user: discord.User = None, filter_name: str = "random"):
        """ Apply a filter to a user's avatar """
        if user is None:
            user = ctx.author
        return await self._filter_command(ctx, user.avatar, filter_name)

    @filter.command(name="image")
    @app_commands.describe(image="The image to apply the filter on", filter_name="The name of the filter to apply")
    @app_commands.choices(filter_name=FILTER_CHOICES)
    async def filter_image(self, ctx: commands.Context, image: discord.Attachment, filter_name: str = "random"):
        """ Apply a filter to a provided image """
        return await self._filter_command(ctx, image, filter_name)


async def setup(bot: bot_data.Bot):
    await bot.add_cog(Images(bot))
