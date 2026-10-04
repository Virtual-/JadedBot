import asyncio
import discord
import yt_dlp as youtube_dl
import os
from gtts import gTTS
from discord.ext import commands
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/tmp/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': True,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  # Needed to stop corrupted packets bringing music to a halt
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


def strip_playlist_param(url):
    """Strip playlist query params from a single-video YouTube link."""
    parsed = urlparse(url)
    if 'youtu' not in parsed.netloc.lower() or parsed.path == '/playlist':
        return url

    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
             if k not in ('list', 'index', 'start_radio')]
    return urlunparse(parsed._replace(query=urlencode(query)))


class YTDLSource(discord.PCMVolumeTransformer):
    """This class is a setup to stream audio into discord."""
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        # Use get_running_loop() instead of deprecated get_event_loop()
        loop = loop or asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def probe(cls, query):
        """Resolve metadata for a search term / URL without downloading. Returns a list of track dicts (more than one when a playlist is given).
        """
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

        if data is None:
            return []

        entries = data['entries'] if 'entries' in data else [data]
        tracks = []
        for entry in entries:
            if not entry:
                continue
            tracks.append({
                'title': entry.get('title', 'Unknown title'),
                'url': entry.get('webpage_url') or entry.get('url') or query,
            })
        return tracks


class Music(commands.Cog):
    """This class is responsible for joining, leaving and various audio channel functionality."""
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}             # guild_id -> list of track dicts waiting to play
        self.now_playing = {}        # guild_id -> the track dict currently playing
        self.pending_playlists = {}  # (guild_id, user_id) -> list of track dicts awaiting !yes

    def get_queue(self, guild_id):
        return self.queues.setdefault(guild_id, [])

    async def play_next(self, guild, channel):
        """Pull the next track off the guild's queue and start playing it."""
        queue = self.get_queue(guild.id)
        voice = guild.voice_client

        if voice is None or not queue:
            self.now_playing.pop(guild.id, None)
            return

        track = queue.pop(0)
        try:
            player = await YTDLSource.from_url(track['url'], stream=True)
        except Exception as e:
            await channel.send(":warning: Couldn't play **{}** ({}). Skipping.".format(track['title'], e))
            print(f"[play_next error] {e}")
            return await self.play_next(guild, channel)

        self.now_playing[guild.id] = track
        voice.play(player, after=lambda e: self._after_track(e, guild, channel))
        await channel.send(':musical_note: Now playing: **{}** :100:'.format(player.title))

    def _after_track(self, error, guild, channel):
        """Runs on a worker thread once a track finishes; hops back to the loop."""
        if error:
            print('Player error: %s' % error)

        future = asyncio.run_coroutine_threadsafe(self.play_next(guild, channel), self.bot.loop)
        try:
            future.result()
        except Exception as e:
            print('Error advancing queue: %s' % e)

    @commands.command()
    async def join(self, ctx, channel: discord.VoiceChannel = None):
        """!join - Joins your current voice channel."""
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel.")
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client

        if voice_client is not None:
            if voice_client.channel == voice_channel:
                await ctx.send("I'm already in your channel.")
            else:
                await voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect(self_deaf=True)

    @commands.command(aliases=['ytplay'])
    async def stream(self, ctx, *, url):
        """!stream <search/URL> - Streams the track, or queues it if something is already playing."""
        try:
            url = strip_playlist_param(url)
            async with ctx.typing():
                tracks = await YTDLSource.probe(url)

            if not tracks:
                await ctx.send("Couldn't find anything for `{}`.".format(url))
                return

            if ctx.voice_client is None:
                await ctx.send("Not connected to a voice channel.")
                return

            for track in tracks:
                track['requester'] = ctx.author.display_name

            if len(tracks) > 1:
                self.pending_playlists[(ctx.guild.id, ctx.author.id)] = tracks
                await ctx.send(
                    ":cd: That's a playlist with **{}** tracks. Type `!yes` to queue all of "
                    "them, or `!no` to just play **{}**.".format(len(tracks), tracks[0]['title']))
                return

            self._queue_tracks(ctx.guild.id, tracks)

            queue = self.get_queue(ctx.guild.id)
            voice = ctx.voice_client
            already_active = voice.is_playing() or voice.is_paused()

            if already_active:
                await ctx.send(':page_with_curl: Queued **{}** (position {}).'.format(
                    tracks[0]['title'], len(queue)))
            else:
                await self.play_next(ctx.guild, ctx.channel)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"[stream error] {e}")

    def _queue_tracks(self, guild_id, tracks):
        """Append tracks to a guild's queue; they play one after another via play_next."""
        self.get_queue(guild_id).extend(tracks)

    @commands.command(name='yes')
    async def confirm_playlist(self, ctx):
        """!yes - Confirms queuing the playlist found by your last !stream."""
        tracks = self.pending_playlists.pop((ctx.guild.id, ctx.author.id), None)

        if not tracks:
            await ctx.send("There's no playlist waiting on your confirmation.")
            return

        if ctx.voice_client is None:
            await ctx.send("Not connected to a voice channel.")
            return

        voice = ctx.voice_client
        already_active = voice.is_playing() or voice.is_paused()

        self._queue_tracks(ctx.guild.id, tracks)
        await ctx.send(':white_check_mark: Queued **{}** tracks from the playlist.'.format(len(tracks)))

        if not already_active:
            await self.play_next(ctx.guild, ctx.channel)

    @commands.command(name='no')
    async def decline_playlist(self, ctx):
        """!no - Declines the pending playlist and plays just the first track instead."""
        tracks = self.pending_playlists.pop((ctx.guild.id, ctx.author.id), None)

        if not tracks:
            await ctx.send("There's no playlist waiting on your confirmation.")
            return

        if ctx.voice_client is None:
            await ctx.send("Not connected to a voice channel.")
            return

        track = tracks[0]
        voice = ctx.voice_client
        already_active = voice.is_playing() or voice.is_paused()

        self._queue_tracks(ctx.guild.id, [track])
        queue = self.get_queue(ctx.guild.id)

        if already_active:
            await ctx.send(':page_with_curl: Queued **{}** (position {}).'.format(track['title'], len(queue)))
        else:
            await self.play_next(ctx.guild, ctx.channel)

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        """!skip - Skips to the next track in the queue."""
        voice = ctx.voice_client
        if voice is None or not (voice.is_playing() or voice.is_paused()):
            await ctx.send("Nothing is playing.")
            return

        await ctx.send(":fast_forward: Skipped.")
        voice.stop()  # triggers the after-callback, which starts the next track

    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx):
        """!queue - Shows what's playing now and what's coming up."""
        queue = self.get_queue(ctx.guild.id)
        current = self.now_playing.get(ctx.guild.id)

        if not current and not queue:
            await ctx.send("The queue is empty. Add something with `!stream`.")
            return

        embed = discord.Embed(title="\N{MUSICAL NOTE} Music Queue", colour=discord.Colour.blurple())

        if current:
            embed.add_field(
                name="Now Playing",
                value="**{}** — added by {}".format(current['title'], current.get('requester', 'someone')),
                inline=False)

        if queue:
            shown = queue[:10]
            lines = ["`{}.` **{}** — {}".format(i, t['title'], t.get('requester', 'someone'))
                     for i, t in enumerate(shown, 1)]
            if len(queue) > len(shown):
                lines.append("…and {} more".format(len(queue) - len(shown)))
            embed.add_field(name="Up Next ({})".format(len(queue)), value="\n".join(lines), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='pause')
    async def _pause(self, ctx):
        """!pause - Pauses the current playing track."""
        voice = ctx.voice_client
        if voice is None or not voice.is_playing():
            await ctx.send("Nothing is playing.")
            return
        voice.pause()
        await ctx.send(":pause_button: Paused current track.")

    @commands.command(name='resume')
    async def _resume(self, ctx):
        """!resume - Resumes the current paused track."""
        voice = ctx.voice_client
        if voice is None or not voice.is_paused():
            await ctx.send("Nothing is paused.")
            return
        voice.resume()
        await ctx.send(":arrow_forward: Resuming current track.")

    @commands.command()
    async def tts(self, ctx, *arguments):
        """!tts <text> - Text to speech."""

        full_string = ""

        for element in arguments:
            full_string = full_string + " " + element

        myobj = gTTS(text=full_string)
        if os.name != 'nt':
            myobj.save('/tmp/tts.mp3')
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('/tmp/tts.mp3'))
        else:
            myobj.save('./tmp/tts.mp3')
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('./tmp/tts.mp3'))

        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

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
        """!stop - Stops playback and clears the queue."""
        self.get_queue(ctx.guild.id).clear()
        self.now_playing.pop(ctx.guild.id, None)

        if ctx.voice_client is not None:
            ctx.voice_client.stop()

        await ctx.send(":stop_button: Stopped and cleared the queue.")

    @stream.before_invoke
    async def ensure_voice(self, ctx):
        print(f"[ensure_voice] voice_client: {ctx.voice_client}")
        print(f"[ensure_voice] author.voice: {ctx.author.voice}")

        if ctx.voice_client is not None:
            # Already connected — nothing to do. (Don't stop playback here; that breaks queueing.)
            return

        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

        try:
            # Use connect()'s own timeout — never wrap it in asyncio.wait_for(),
            # that deadlocks on cancellation cleanup in discord.py.
            await ctx.author.voice.channel.connect(self_deaf=True, timeout=15.0, reconnect=True)
            print("[ensure_voice] connected successfully")
        except asyncio.TimeoutError:
            await ctx.send("Timed out trying to join the voice channel.")
            print("[ensure_voice] connection timed out")
            raise commands.CommandError("Voice connect timed out.")
        except discord.ClientException as e:
            # e.g. "Already connected to a voice channel." from a stale client
            print(f"[ensure_voice] ClientException: {e}")
            if ctx.voice_client is None:
                await ctx.send(f"Couldn't join voice: {e}")
                raise commands.CommandError(str(e))
        except Exception as e:
            await ctx.send(f"Couldn't join voice: {e}")
            print(f"[ensure_voice] connect error: {e!r}")
            raise commands.CommandError(str(e))

    @commands.command()
    async def leave(self, ctx):
        """!leave - Leaves the channel."""
        if ctx.guild is not None:
            self.get_queue(ctx.guild.id).clear()
            self.now_playing.pop(ctx.guild.id, None)
        try:
            await ctx.voice_client.disconnect()
        except AttributeError:
            await ctx.send("I'm not currently in a voice channel.")


async def setup(bot):
    await bot.add_cog(Music(bot))
