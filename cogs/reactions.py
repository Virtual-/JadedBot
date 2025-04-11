import discord
import sqlite3
import requests
from discord.ext import commands
from PIL import Image
from io import BytesIO

con = sqlite3.connect('reactions.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS reactions
                    (command text PRIMARY KEY, filename text)''')
con.commit()
con.close()

class Reactions(commands.Cog):
    """This class is responsible for reactions pics and gifs"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['r'])
    async def reaction(self, ctx, command: str):
        con = sqlite3.connect('reactions.db')
        cur = con.cursor()
        cur.execute("SELECT filename FROM reactions WHERE command = ?", (command,))
        result = cur.fetchone()
        file_path = result[0]
        con.close()
        await ctx.send(file=discord.File(file_path))

    @commands.command()
    async def reactionlist(self, ctx):
        con = sqlite3.connect('reactions.db')
        cur = con.cursor()
        cur.execute("SELECT command FROM reactions")
        rows = cur.fetchall()
        formatted = "\n".join(f"!r {row[0]}" for row in rows)
        message = f'''```{formatted}```'''
        await ctx.send(message)
        con.close()

    @commands.command()
    async def reactionadd(self, ctx, name: str, url: str):
        url = url

        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

        format = img.format.lower()
        filename = f"{name}.{format}"
        img.save(f"assets/{filename}")

        con = sqlite3.connect('reactions.db')
        cur = con.cursor()
        cur.execute("INSERT INTO reactions (command, filename) VALUES (?, ?)", (name, "assets/" + filename))
        con.commit()
        con.close()

  
async def setup(bot):
    await bot.add_cog(Reactions(bot))
