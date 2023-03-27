import requests
import discord
from discord.ext import commands
from bs4 import BeautifulSoup

class WoW(commands.Cog):
    """This class/cog is responsible for searching Warcraft items and pasting into chat"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def wow(self, ctx, *, search):
        """!wow <search> - Searches wowdb and returns the result."""
        url = 'https://www.wowdb.com/search?search='
        query = search.replace(' ', '+')

        try:
            page = requests.get(url + query).text
            soup = BeautifulSoup(page, 'html.parser')
            result = soup.find(class_="even")
            end_url = str(result.select_one("a")['href'])
            #wowhead = soup.find('a', {'rel':'nofollow'})

            await ctx.send('WoWDB Link:')
            await ctx.send(end_url)
        except:
            await ctx.send('Failed to find that page, sorry.')
            print(wowhead['href'])



async def setup(bot):
    await bot.add_cog(WoW(bot))
