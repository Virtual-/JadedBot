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
        if wiki == 'ck2':
            end_url = 'https://ck2.paradoxwikis.com'
            query_url = 'https://ck2.paradoxwikis.com/index.php?search={0}&title=Special:Search&profile=default&fulltext=1'.format(search.replace(" ", "+"))
        if wiki == 'ck3':
            end_url = 'https://ck3.paradoxwikis.com'
            query_url = 'https://ck3.paradoxwikis.com/index.php?search={0}&title=Special:Search&profile=default&fulltext=1'.format(search.replace(" ", "+"))
        if wiki == 'rs':
            end_url = 'https://oldschool.runescape.wiki'
            query_url = 'https://oldschool.runescape.wiki/w/Special:Search?search={0}&profile=default&fulltext=1&searchToken=996oaxfbkyqcf1jz9bfg90ms9'.format(search.replace(" ", "+"))
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


    @commands.command(aliases=['rs'])
    async def runescape(self, ctx, *, search):
        """!runescape, !rs <search> - Searched the OSRS wiki."""
        rs_string = self.wiki_search(search, 'rs')
        await ctx.send('' + rs_string)
    

    @commands.command(aliases=['ha'])
    async def highalch(self, ctx, *, searcheditem):
        data = requests.get("https://prices.runescape.wiki/api/v1/osrs/mapping").text
        items = json.loads(data)
        for item in items:
            if searcheditem.capitalize() in item['name']:
                data = requests.get("https://oldschool.runescape.wiki/w/File:{0}".format(item['icon'].replace(' ', '_'))).text
                soup = BeautifulSoup(data, 'html.parser')
                myclass = soup.find("div", {"class": "fullImageLink"})
                end_url = myclass.find('a')['href']
                await ctx.send('' + 'https://oldschool.runescape.wiki' + end_url)
                await ctx.send("``` **{0}**\nHigh Alchemy price: {1}\n{2}```".format(str(item['name']), str(item['highalch']), str(item['examine'])))


    @commands.command()
    async def ck2(self, ctx, *, search):
        """!ck2 <search> - Searches the CK2 wiki."""
        ck_string = self.wiki_search(search, 'ck2')
        await ctx.send('' + ck_string)


    @commands.command()
    async def ck3(self, ctx, *, search):
        """!ck3 <search> - Searches the CK3 wiki."""
        ck_string = self.wiki_search(search, 'ck3')
        await ctx.send('' + ck_string)


async def setup(bot):
    await bot.add_cog(WikiSearch(bot))
