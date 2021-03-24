import discord
import os
import git
from discord.ext import commands

JADEDVER = 1.5
COMMITID = git.Repo().head.object.hexsha[:7]

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),description="Jaded Bot")

@bot.command()
async def version(ctx):
    """!version - Displays information about this verison of JadedBot"""
    await ctx.send("JadedBot - https://github.com/Virtual-/JadedBot")
    await ctx.send("Version - {0}".format(JADEDVER))
    await ctx.send("Latest commit - https://github.com/Virtual-/JadedBot/commit/{0}".format(COMMITID))


@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    """!load <module> - Loads a python module into the bot"""
    bot.load_extension(f'cogs.{extension}')


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    """!unload <module> - Unloads a python module into the bot"""
    bot.unload_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


print("JadedBot - https://github.com/Virtual-/JadedBot\nVersion - {1}\nLatest commit - https://github.com/Virtual-/JadedBot/commit/{0}".format(COMMITID, JADEDVER))
bot.run('ODI0MDE5MzAzMjc1NjkyMDQ0.YFpRxw.ovr_nYChQfNNZwbYsChsYLVj1Tk')
