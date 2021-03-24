import discord
import praw
import configparser
from random import randint
from discord.ext import commands

class Reddit(commands.Cog):
    """This class is responsible for all the reddit functionality."""

    def __init__(self, bot):
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read('configfile')
        self.REDDIT_ID = self.config['JadedBot']['REDDIT_ID']
        self.REDDIT_SECRET = self.config['JadedBot']['REDDIT_SECRET']

    @commands.command()
    async def shitpost(self, ctx):
        """!shitpost - Grabs a random post from /r/copypasta"""
        reddit = praw.Reddit(client_id=self.REDDIT_ID, client_secret=self.REDDIT_SECRET, user_agent="jadedbot")
        random_num = randint(0, 99)
        submission = reddit.subreddit("copypasta").hot(limit=100)
        for i, post in enumerate(submission):
            if i == random_num:
                try:
                    await ctx.send(post.title)
                    await ctx.send(post.selftext)
                except:
                    #await ctx.send('An error occured sending the post (too long) try again.')
                    full_str = str(post.selftext)
                    #print(type(len(full_str)))
                    firstpart, secondpart = full_str[:1999], full_str[1999:]
                    await ctx.send(firstpart)
                    await ctx.send(secondpart)


    @commands.command()
    async def greentext(self, ctx):
        """!greentext - Grabs a random post from /r/greentext"""
        reddit = praw.Reddit(client_id=self.REDDIT_ID, client_secret=self.REDDIT_SECRET, user_agent="jadedbot")
        random_num = randint(0, 99)
        submission = reddit.subreddit("greentext").hot(limit=100)
        for i, post in enumerate(submission):
            if i == random_num:
                try:
                    await ctx.send(post.url)
                except:
                    await ctx.send('An error occured sending the image try again.')



def setup(bot):
    bot.add_cog(Reddit(bot))
