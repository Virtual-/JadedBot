import discord
import os
import configparser
from discord.ext import commands

JADEDVER = 2.1
COMMITID = ""

if os.name != 'nt':
    import git
    COMMITID = git.Repo().head.object.hexsha[:7]

config = configparser.ConfigParser()
config.read('configfile')
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),description="Jaded Bot")

@bot.command()
async def version(ctx):
    """!version - Displays information about this verison of JadedBot"""
    await ctx.send("JadedBot - https://github.com/Virtual-/JadedBot")
    await ctx.send("Version - {0}".format(JADEDVER))
    if os.name != 'nt':
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
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
        except Exception as e:
            print("Had an issue loading {0} module. Skipping".format(filename))
            print(e)

if os.path.isfile('configfile'):
    pass
else:
    print("\nCan't see 'configfile' generating blank configfile...")
    f = open("configfile", "w")
    f.write("[JadedBot]\nTOKEN =\nREDDIT_ID =\nREDDIT_SECRET =\n")

print("\n")
if os.name != 'nt':
    print("JadedBot - https://github.com/Virtual-/JadedBot\nVersion - {1}\nLatest commit - https://github.com/Virtual-/JadedBot/commit/{0}".format(COMMITID, JADEDVER))
else:
    print("JadedBot - https://github.com/Virtual-/JadedBot\nVersion - {0}\nRunning on Windows.".format(JADEDVER))

try:
    config['JadedBot']['TOKEN']
except KeyError:
    print("\nYou seem to be missing the discord key for the bot, please add this to configfile\n\n")

bot.run(config['JadedBot']['TOKEN'])
