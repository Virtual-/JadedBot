import discord
import json
from random import randint
#from youtubesearchpython import SearchVideos
from discord.ext import commands


class YouTube(commands.Cog):
    """This class is responsible for some youtube functionality, mainly searching."""
    def __init__(self, bot):
        self.bot = bot


    #@commands.command()
    #async def youtube(self, ctx, *, search):
    #    """!youtube <search> - Searches youtube with your search and returns the top link."""
    #    search = SearchVideos(search, offset = 1, mode = "json", max_results = 1)
    #    result = search.result()
    #    result = json.loads(result)
    #    await ctx.send(result['search_result'][0]['title'] + " " + str(result['search_result'][0]['views']) + " views")
    #    await ctx.send(result['search_result'][0]['link'])


    #@commands.command()
    #async def vaporwave(self, ctx):
    #    """!vaporwave - Searches youtube for vaporwave."""
    #    search = SearchVideos('vaporwave', offset = 1, mode = "json", max_results = 25)
    #    result = search.result()
    #    result = json.loads(result)
    #    index = randint(1, 24)
    #    await ctx.send(result['search_result'][index]['title'] + " " + str(result['search_result'][index]['views']) + " views")
    #    await ctx.send(result['search_result'][index]['link'])


async def setup(bot):
    await bot.add_cog(YouTube(bot))
