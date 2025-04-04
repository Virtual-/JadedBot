import discord
import os
import configparser
import asyncio
from discord.ext import commands

JADEDVER = 2.4
COMMITID = ""

if os.name != 'nt':
    import git
    COMMITID = git.Repo().head.object.hexsha[:7]

config = configparser.ConfigParser()
config.read('configfile')
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


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

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state is None:
        return
    if len(voice_state.channel.members) == 1:
        await voice_state.disconnect()

if os.path.isfile('configfile'):
    pass
else:
    print("\nCan't see 'configfile' generating blank configfile...")
    f = open("configfile", "w")
    f.write("[JadedBot]\nTOKEN =\nREDDIT_ID =\nREDDIT_SECRET =\n")
    f.close()


print("\n")
if os.name != 'nt':
    print("JadedBot - https://github.com/Virtual-/JadedBot\nVersion - {1}\nLatest commit - https://github.com/Virtual-/JadedBot/commit/{0}".format(COMMITID, JADEDVER))
else:
    print("JadedBot - https://github.com/Virtual-/JadedBot\nVersion - {0}\nRunning on Windows.".format(JADEDVER))

try:
    config['JadedBot']['TOKEN']
except KeyError:
    print("\nYou seem to be missing the discord key for the bot, please add this to configfile\n\n")

async def main():
    async with bot:
        await bot.load_extension(f'cogs.music')
        await bot.load_extension(f'cogs.reactions')
        await bot.load_extension(f'cogs.reddit')
        await bot.load_extension(f'cogs.sounds')
        await bot.load_extension(f'cogs.wikisearch')
        await bot.load_extension(f'cogs.wow')
        await bot.start(config['JadedBot']['TOKEN'])

asyncio.run(main())
