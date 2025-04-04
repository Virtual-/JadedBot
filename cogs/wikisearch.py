import discord
import requests
import json
from discord.ext import commands
from bs4 import BeautifulSoup

class WikiSearch(commands.Cog):
    """This class/cog is responsible for searching various different game wiki's"""
    def __init__(self, bot):
        self.bot = bot


    def wiki_search(self, search, wiki):
        if wiki == 'everquest':
            end_url = 'https://wiki.project1999.com'
            query_url = 'https://wiki.project1999.com/index.php?title=Special%3ASearch&search={0}&fulltext=Search'.format(search.replace(" ", "+"))
        try:
            page = requests.get(query_url, verify=False).text
            soup = BeautifulSoup(page, 'html.parser')
            result = soup.find(class_="mw-search-result-heading")
            end_string = str(result.select_one("a")['href'])
            return end_url + end_string
        except AttributeError:
            return "Failed to find that page, Sorry."


    @commands.command(aliases=['eq'])
    async def everquest(self, ctx, *, search):
        """!everquest, !eq <search> - Searches the Project1999 wiki."""
        eq_string = self.wiki_search(search, 'everquest')
        await ctx.send('' + eq_string)


async def setup(bot):
    await bot.add_cog(WikiSearch(bot))
