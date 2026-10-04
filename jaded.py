import discord
import os
import configparser
import asyncio
import importlib.util
from discord.ext import commands

#import logging
#
#logging.basicConfig(level=logging.DEBUG)
#
#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.StreamHandler()
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)


JADEDVER = 2.5
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
    await bot.load_extension(f'cogs.{extension}')


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    """!unload <module> - Unloads a python module into the bot"""
    await bot.unload_extension(f'cogs.{extension}')

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
    f.write("[JadedBot]\nTOKEN =\n\n[OptionalCogs]\nmonsters = false\n")
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


LOCKFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.jaded.lock')
_lock_handle = None


def acquire_single_instance_lock():
    """Refuse to start if another copy of the bot is already running here.

    Two JadedBot processes signed in with the same token each receive every
    message from the gateway, so both run the command and both reply. That
    reads as the bot posting everything twice, which is most obvious with
    !r because the duplicate is a whole image. Holding an exclusive lock on
    .jaded.lock means the second copy stops here instead.
    """
    global _lock_handle
    _lock_handle = open(LOCKFILE, 'w')
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(_lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(_lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("\nJadedBot is already running from this directory, so this copy is exiting.")
        print("Two copies on the same token answer every command twice.")
        print("Find the running one with: pgrep -af jaded.py\n")
        raise SystemExit(1)
    _lock_handle.write(str(os.getpid()))
    _lock_handle.flush()


# AWFUL ghetto workaround for issue in yt_dlp right now. Needs removal at some point. Monkeypatched to keep running.
import yt_dlp.extractor.youtube.pot._provider as provider

def patched_bug_reports_message(before=''):
        return "Please report bugs at https://github.com/yt-dlp/yt-dlp/issues"

provider.bug_reports_message = patched_bug_reports_message


OPTIONAL_COGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cogs-optional')


async def load_optional_cogs(bot):
    """Load cogs from cogs-optional/, each gated by its own [OptionalCogs] key
    in configfile (off unless a user explicitly turns it on). These aren't part
    of the core bot - separate directory, separate opt-in, so a rough or
    experimental cog never loads unless someone asks for it."""
    if not os.path.isdir(OPTIONAL_COGS_DIR):
        return

    for filename in sorted(os.listdir(OPTIONAL_COGS_DIR)):
        if not filename.endswith('.py') or filename.startswith('_'):
            continue
        name = filename[:-3]

        if not config.getboolean('OptionalCogs', name, fallback=False):
            print(f"[optional cogs] {name} is disabled (enable it under [OptionalCogs] in configfile)")
            continue

        path = os.path.join(OPTIONAL_COGS_DIR, filename)
        spec = importlib.util.spec_from_file_location(f'cogs_optional.{name}', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        await module.setup(bot)
        print(f"[optional cogs] {name} loaded")


async def main():
    async with bot:
        await bot.load_extension(f'cogs.music')
        await bot.load_extension(f'cogs.reactions')
        await bot.load_extension(f'cogs.sounds')
        await bot.load_extension(f'cogs.wikisearch')
        await bot.load_extension(f'cogs.wow')
        await bot.load_extension(f'cogs.help')
        await load_optional_cogs(bot)
        await bot.start(config['JadedBot']['TOKEN'])


acquire_single_instance_lock()
asyncio.run(main())
