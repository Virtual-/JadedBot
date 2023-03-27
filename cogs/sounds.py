import discord
from discord.ext import commands

class Sounds(commands.Cog):
    """This class is responsible for playing locally saved soundbites from the assets folder."""
    def __init__(self, bot):
        self.bot = bot


    async def play(self, ctx, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)


    @commands.command(aliases=['nobody'])
    async def nobodyhere(self, ctx):
        """!nobodyhere, !nobody - Plays nobody here."""
        await self.play(ctx, "assets/nobody.webm")


    @commands.command()
    async def anime(self, ctx):
        """!anime - Plays the WOW sound."""
        await self.play(ctx, "assets/anime.webm")


    @commands.command()
    async def poopsock(self, ctx):
        """!poopsock - Plays when mom find poopsock."""
        await self.play(ctx, "assets/poopsock.webm")


    @commands.command()
    async def betterpoop(self, ctx):
        """!betterpoop - Plays when mom find poopsock better version."""
        await self.play(ctx, "assets/poopsockbetter.webm")


    @commands.command()
    async def ding(self, ctx):
        """!ding - Plays the ding sound effect."""
        await self.play(ctx, "assets/ding.webm")


    @commands.command()
    async def popping(self, ctx):
        """!popping - Plays the whats popping sound effect."""
        await self.play(ctx, "assets/popping.mp3")


    @commands.command(alises=['ram'])
    async def ramranch(self, ctx):
        """!ramranch, !ram - Plays ram ranch."""
        await self.play(ctx, "assets/ram.webm")


    @commands.command()
    async def ram85(self, ctx):
        """!ram85 - Plays ram ranch 85"""
        await self.play(ctx, "assets/ram85.webm")


    @commands.command()
    async def nice(self, ctx):
        """!nice - Plays the nice sound effect."""
        await self.play(ctx, "assets/nice.webm")


    @commands.command()
    async def sorry(self, ctx):
        """!sorry - Plays the sorry for what sound effect."""
        await self.play(ctx, "assets/sorryforwhat.mp3")


    @commands.command()
    async def excellent(self, ctx):
        """!excellent - Plays the excellent sound effect."""
        await self.play(ctx, "assets/excellent.webm")


    @commands.command()
    async def augh(self, ctx):
        """!augh - Plays the tim allen sound effect."""
        await self.play(ctx, "assets/timallen.webm")


    @commands.command()
    async def trap1(self, ctx):
        """!trap1 - Plays the first trapaholics sound effect."""
        await self.play(ctx, "assets/trap1.wav")


    @commands.command()
    async def trap2(self, ctx):
        """!trap2 - Plays the second trapaholics sound effect."""
        await self.play(ctx, "assets/trap2.wav")


    @commands.command()
    async def trap3(self, ctx):
        """!trap3 - Plays the first trapaholics sound effect."""
        await self.play(ctx, "assets/trap3.wav")


    @commands.command()
    async def trap4(self, ctx):
        """!trap4 - Plays the first trapaholics sound effect."""
        await self.play(ctx, "assets/trap4.wav")


    @commands.command()
    async def maybach(self, ctx):
        """!maybach - Plays the Maybach music sound effect."""
        await self.play(ctx, "assets/maybach.wav")


    @commands.command()
    async def rack(self, ctx):
        """!rack - Plays beautiful rack."""
        await self.play(ctx, "assets/rack.webm")
        
    @commands.command()
    async def toasty(self, ctx):
        """!toasty - Toasty."""
        await self.play(ctx, "assets/toasty.mp3")

    @commands.command()
    async def plug(self, ctx):
        """!plug - Plug."""
        await self.play(ctx, "assets/plug.mp3")


async def setup(bot):
    await bot.add_cog(Sounds(bot))
