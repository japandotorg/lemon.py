from aiohttp import ClientSession

from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.member import Member
from nextcord.ext.commands.bot import Bot

class Actions(commands.Cog):
    " Fun action commands like hug/pat "
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('`Actions` cog has been loaded')
        
    @commands.command()
    async def hug(self, ctx: commands.Context, *, member: Member = None):
        """  Sends a random anime hugging gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/hug") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} hugs {member.name}",
                        color=0x800080
                    )
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return
    
    @commands.command()
    async def kiss(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime kissing gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/kiss") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} kisses {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return
    
    @commands.command()
    async def pat(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime pat gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/pat") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} pats {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return
    
    @commands.command()
    async def slap(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime slapping gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/slap") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} slaps {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return
    
    @commands.command()
    async def tickle(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime tickling gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/tickle") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} tickles {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return
    
    @commands.command()
    async def cuddle(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime cuddling gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/cuddle") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} cuddles {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command()
    async def poke(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime poking gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/poke") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} pokes {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command()
    async def smug(self, ctx: commands.Context, *, member: Member = None):
        """ Sends a random anime smug gif """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/smug") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} is smug at {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return
    
def setup(bot):
    bot.add_cog(Actions(bot))