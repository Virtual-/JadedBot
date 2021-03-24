import discord
from discord.ext import commands


class Reactions(commands.Cog):
    """This class is responsible for reactions pics and gifs"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def audiophile(self, ctx):
        """!audiophile - Places audiophile image into chat."""
        await ctx.send(file=discord.File('assets/audiophile.jpg'))


def setup(bot):
    bot.add_cog(Reactions(bot))
