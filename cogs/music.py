import asyncio
import discord
import youtube_dl
import os
from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/tmp/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {}

if os.name != 'nt': # This if statement is needed because Windows can't into environment variables properly. LOL.
    ffmpeg_options = {
        'options': '-vn',
    }
else: 
        ffmpeg_options = {
        'options': '-vn',
        'executable': 'C:\\ffmpeg\\bin\\ffmpeg.exe' # Lame hardcoded PATH but env variables don't seem to work.
    }

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, channel: discord.VoiceChannel="Default Voice Channel"): # This seems to failover and make the bot join your current channel
        """!join <channelname> - Joins the channel."""

        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except AttributeError:
            await ctx.send("You're not in a channel.")


    @commands.command()
    async def ytplay(self, ctx, *, url):
        """!ytplay <search/URL> - Downloads and plays the requested URL or search term."""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """!stream <search/URL> - Directly streams the requested URL or search term. (Can be buggy)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """!volume <number> - Changes the volume of the audio."""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if volume > 100:
            return await ctx.send("Volume can't go higher than 100.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """!stop - Stops and disconnects the bot from voice."""

        ctx.voice_client.stop()

    #@play.before_invoke
    @ytplay.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


    @commands.command()
    async def leave(self, ctx):
        """!leave - Leaves the channel."""
        try:
            await ctx.voice_client.disconnect()
        except AttributeError:
            await ctx.send("I'm not currently in a voice channel.")


def setup(bot):
    bot.add_cog(Music(bot))
