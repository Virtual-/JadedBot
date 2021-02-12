import os
import discord
import requests
import json
import praw
import configparser
import youtube_dl
from jones import quotes
from random import randint
from youtubesearchpython import SearchVideos
from discord.ext import commands
from bs4 import BeautifulSoup

class JadedBot(commands.Bot):
    def __init__(self, bot):
        super().__init__(command_prefix='!')
        self.config = configparser.ConfigParser()
        self.config.read('configfile')

        self.TOKEN = self.config['JadedBot']['TOKEN']
        self.REDDIT_ID = self.config['JadedBot']['REDDIT_ID']
        self.REDDIT_SECRET = self.config['JadedBot']['REDDIT_SECRET']
        self.command(aliases=['yt'])(self.youtube) # Need to tidy this up and make it modular.
        self.command(aliases=['eq'])(self.everquest)
        self.command()(self.ck2)
        self.command()(self.ck3)
        self.command()(self.rs)
        self.command()(self.vaporwave)
        self.command()(self.shitpost)
        self.command()(self.greentext)
        self.command()(self.redpill)
        self.command()(self.join)
        self.command()(self.leave)
        self.command(aliases=['nobody'])(self.nobodyhere)
        self.command()(self.audiophile)
        self.command()(self.ding)
        self.command()(self.jaded)
        self.command()(self.stop)
        self.command()(self.pause)
        self.command()(self.play)
        self.command(aliases=['wow'])(self.anime)
        self.command()(self.popping)
        self.command(aliases=['ram'])(self.ramranch)
        self.command(aliases=['ram85'])(self.ramranch85)
        self.command()(self.nice)
        self.command()(self.poopsock)
        self.command(aliases=['sorryforwhat'])(self.sorry)
        self.command()(self.excellent)
        self.command()(self.betterpoop)
        self.command()(self.augh)
        #self.command()(self.ytplay)
     
     
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
            page = requests.get(query_url).text
            soup = BeautifulSoup(page, 'html.parser')
            result = soup.find(class_="mw-search-result-heading")
            end_string = str(result.select_one("a")['href'])
            return end_url + end_string
        except AttributeError:
            return "Failed to find that page, Sorry."
    
    
    async def everquest(self, ctx, *, search):
        eq_string = self.wiki_search(search, 'everquest')
        await ctx.send('' + eq_string)
        
        
    async def rs(self, ctx, *, search):
        rs_string = self.wiki_search(search, 'rs')
        await ctx.send('' + rs_string)
    
           
    async def youtube(self, ctx, *, search):
        search = SearchVideos(search, offset = 1, mode = "json", max_results = 1)
        result = search.result()
        result = json.loads(result)
        await ctx.send(result['search_result'][0]['title'] + " " + str(result['search_result'][0]['views']) + " views")
        await ctx.send(result['search_result'][0]['link'])
     
     
    async def ck2(self, ctx, *, search):
        ck_string = self.wiki_search(search, 'ck2')
        await ctx.send('' + ck_string)
        

    async def ck3(self, ctx, *, search):
        ck_string = self.wiki_search(search, 'ck3')
        await ctx.send('' + ck_string)
        
    
    async def vaporwave(self, ctx):
        search = SearchVideos('vaporwave', offset = 1, mode = "json", max_results = 25)
        result = search.result()
        result = json.loads(result)
        index = randint(1, 24)
        await ctx.send(result['search_result'][index]['title'] + " " + str(result['search_result'][index]['views']) + " views")
        await ctx.send(result['search_result'][index]['link'])
    
    
    async def shitpost(self, ctx):
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
    
    
    async def greentext(self, ctx):
        reddit = praw.Reddit(client_id=self.REDDIT_ID, client_secret=self.REDDIT_SECRET, user_agent="jadedbot")
        random_num = randint(0, 99)
        submission = reddit.subreddit("greentext").hot(limit=100)
        for i, post in enumerate(submission):
            if i == random_num:
                try:
                    await ctx.send(post.url)
                except:
                    await ctx.send('An error occured sending the image try again.')
    
    
    async def redpill(self, ctx):
        random_num = randint(0, len(quotes))
        await ctx.send(quotes[random_num])
    
    
    async def join(self, ctx, channel: discord.VoiceChannel="Jaded Bot Audio Room"):
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except AttributeError:
            await ctx.send("You're not in a channel.")
            
            
    async def leave(self, ctx):
        try:
            await ctx.voice_client.disconnect()
        except AttributeError:
            await ctx.send("I'm not currently in a channel.")
            
            
    async def nobodyhere(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/nobody.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
    
    
    async def anime(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/anime.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    async def poopsock(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/poopsock.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    async def betterpoop(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/poopsockbetter.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    async def audiophile(self, ctx):
        await ctx.send(file=discord.File('assets/audiophile.jpg'))
        
        
    async def ding(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/ding.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
            
    async def jaded(self, ctx):
        await ctx.send('```Command List:\nHelp:\n!jaded - Prints this command list.\n\nWiki Searching:\n!everquest, !eq <search> - Searches P99 Wiki.\n!ck2 <search> - Searches CK2 Wiki.\n!ck3 <search> - Searches CK3 Wiki.\n!rs <search> - Searches OSRS Wiki.\n\nYoutube:\n!youtube, !yt <search> - Searches youtube and returns first video.\n!vaporwave - Returns random vaporwave track.\n\nMisc:\n!shitpost - Professionally shitposts in chat.\n!redpill - Drops some fresh redpills from Alex Jones.\n!audiophile - Inserts man listening to Edd Ed and Eddy Music.\n!greentext - Inserts a random greentext.\n\nAudio Controls:\n!join - Joins the bot to the voice channel you\'re currently in.\n!leave - Leaves the voice channel the bot is currently in.\n!stop - Stops current audio.\n!pause - Pauses current audio.\n!play - Resumes current audio.\n\nSounds:\n!nobodyhere, !nobody - There is nobody here.\n!ding - Plays EQ sound effect.\n!anime, !wow - Plays the woooow anime sound.\n!popping - Whats pawppping.\n!ramranch, !ram - Plays Ram Ranch.\n!ramranch85, !ram85 - Plays Ram Ranch 85\n!nice - Click. Nice.\n!poopsock - Plays when mom find poop sock.\n!sorry - Our daddy told us to never be ashamed of our...```')
        await ctx.send('```Command List:\nHelp:\n!jaded - Prints this command list.\n\nWiki Searching:\n!everquest, !eq <search> - Searches P99 Wiki.\n!ck2 <search> - Searches CK2 Wiki.\n!ck3 <search> - Searches CK3 Wiki.\n!rs <search> - Searches OSRS Wiki.\n\nYoutube:\n!youtube, !yt <search> - Searches youtube and returns first video.\n!vaporwave - Returns random vaporwave track.\n\nMisc:\n!shitpost - Professionally shitposts in chat.\n!redpill - Drops some fresh redpills from Alex Jones.\n!audiophile - Inserts man listening to Edd Ed and Eddy Music.\n!greentext - Inserts a random greentext.\n\nAudio Controls:\n!join - Joins the bot to the voice channel you\'re currently in.\n!leave - Leaves the voice channel the bot is currently in.\n!stop - Stops current audio.\n!pause - Pauses current audio.\n!play - Resumes current audio.\n\nSounds:\n!nobodyhere, !nobody - There is nobody here.\n!ding - Plays EQ sound effect.\n!anime, !wow - Plays the woooow anime sound.\n!popping - Whats pawppping.\n!ramranch, !ram - Plays Ram Ranch.\n!ramranch85, !ram85 - Plays Ram Ranch 85\n!nice - Click. Nice.\n!poopsock - Plays when mom find poop sock.\n!betterpoop - Mom find poopsock better version.\n!augh - AUGH?!.\n!sorry - Sorry for what\n!excellent - Excellent.```')
        
        
    async def stop(self, ctx):
        ctx.voice_client.stop()
    
    
    async def pause(self, ctx):
        ctx.voice_client.pause()
        
        
    async def play(self, ctx):
        ctx.voice_client.resume()
        
    
    #async def ytplay(self, ctx, *, search): # Broken atm because of DMCA on youtube-dl
    #    search = SearchVideos(search, offset = 1, mode = "json", max_results = 1)
    #    result = search.result()
    #    result = json.loads(result)
    #    #ydl_opts = {'outtmpl': '/tmp/track.mpa'}
    #    with youtube_dl.YoutubeDL({'format':'140', 'outtmpl': '/tmp/track.mpa'}) as ydl:
    #        print(result['search_result'][0]['link'])
    #        ydl.download([result['search_result'][0]['link']])
    #        
    #    try:
    #        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('/tmp/track.mpa'))
    #        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    #        ctx.voice_client.source.volume = 30
    #    except AttributeError:
    #        await ctx.send("Join me to a channel with !join first.")
        

    async def popping(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/popping.mp3'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    
    async def ramranch(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/ram.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    
    async def ramranch85(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/ram85.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")


    async def nice(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/nice.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    
    async def sorry(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/sorryforwhat.mp3'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
    async def excellent(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/excellent.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")

    async def augh(self, ctx):
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/timallen.webm'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 30
        except AttributeError:
            await ctx.send("Join me to a channel with !join first.")
            
bot = commands.Bot(command_prefix='!', description="Jaded Bot")
jaded = JadedBot(bot)

jaded.run(jaded.TOKEN)
