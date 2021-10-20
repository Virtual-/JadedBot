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


    @commands.command()
    async def soy(self, ctx):
        """!soy - Places a soyboy image into chat."""
        await ctx.send(file=discord.File('assets/soy.png'))


    @commands.command()
    async def gal(self, ctx):
        """!gal - Places galosengen into chat."""
        await ctx.send(file=discord.File('assets/gal.gif'))

    @commands.command()
    async def smiley(self, ctx):
        """!smiley - Places galosengen into chat."""
        await ctx.send(file=discord.File('assets/smiley.gif'))

def setup(bot):
    bot.add_cog(Reactions(bot))
