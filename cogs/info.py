import time
import asyncio
import logging
import datetime
import nextcord
import speedtest
import concurrent
from nextcord.ext import commands

class Info(commands.Cog):
    """
    Show's bot info and stuff
    """
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('`Info` cog has been loaded')
        
    @commands.bot_has_permissions(embed_links=True)
    @commands.group(invoke_without_command=True)
    async def ping(self, ctx):
        """ Sends bot's ping latency """
        start = time.monotonic()
        message = await ctx.send("Pinging...")
        end = time.monotonic()
        totalPing = round((end - start) * 1000, 2)
        e = nextcord.Embed(
            title="Pinging..",
            description=f"Overall Latency: {totalPing}ms"
        )
        await asyncio.sleep(0.25)
        try:
            await message.edit(
                content=None,
                embed=e
            )
        except nextcord.NotFound:
            return
        
        botPing = round(self.bot.latency * 1000, 2)
        e.description = e.description + f"\nDiscord Websocket Latency: {botPing}ms"
        await asyncio.sleep(0.25)
        
        averagePing = (botPing + totalPing) / 2
        if averagePing >= 1000:
            color = nextcord.Colour.red()
        elif averagePing >= 200:
            color = nextcord.Colour.orange()
        else:
            color = nextcord.Colour.green()
            
        if not self.settings["host_latency"]:
            e.title = "Pong!"
            
        e.color = color
        try:
            await message.edit(embed=e)
        except nextcord.NotFound:
            return
        if not self.settings["host_latency"]:
            return
        
        executor = concurrent.features.ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        try:
            s = speedtest.Speedtest(secure=True)
            await loop.run_in_executor(executor, s.get_servers)
            await loop.run_in_executor(executor, s.get_best_server)
        except Exception as exc:
            host_latency = "`Failed`"
        else:
            result = s.results.dict()
            host_latency = round(result["ping"], 2)
            
        e.title = "Pong!"
        e.description = e.description + f"\nHost Latency: {host_latency}ms"
        await asyncio.sleep(0.25)
        try:
            await message.edit(embed=e)
        except nextcord.NotFound:
            return
        
    @ping.command()
    async def moreinfo(self, ctx: commands.Context):
        """ Ping with additional latency statistics """
        now = datetime.datetime.utcnow().timestamp()
        receival_ping = round((now - ctx.message.created_at.timestamp()) * 1000, 2)
        
        e = nextcord.Embed(
            title="Pinging..",
            description=f"Receival Latency: {receival_ping}ms",
        )
        
        send_start = time.monotonic()
        message = await ctx.send(embed=e)
        send_end = time.monotonic()
        send_ping = round((send_end - send_start) * 1000, 2)
        e.description += f"\nSend Latency: {send_ping}ms"
        await asyncio.sleep(0.25)

        edit_start = time.monotonic()
        try:
            await message.edit(embed=e)
        except nextcord.NotFound:
            return
        edit_end = time.monotonic()
        edit_ping = round((edit_end - edit_start) * 1000, 2)
        e.description += f"\nEdit Latency: {edit_ping}ms"

        average_ping = (receival_ping + send_ping + edit_ping) / 3
        if average_ping >= 1000:
            color = nextcord.Colour.red()
        elif average_ping >= 200:
            color = nextcord.Colour.orange()
        else:
            color = nextcord.Colour.green()

        e.color = color
        e.title = "Pong!"

        await asyncio.sleep(0.25)
        try:
            await message.edit(embed=e)
        except nextcord.NotFound:
            return
        
    @ping.command()
    async def shards(self, ctx: commands.Context):
        """ View latency for all shards. """
        description = []
        latencies = []
        for shard_id, shard in self.bot.shards.items():
            latency = round(shard.latency * 1000, 2)
            latencies.append(latency)
            description.append(f"#{shard_id}: {latency}ms")
        average_ping = sum(latencies) / len(latencies)
        if average_ping >= 1000:
            color = nextcord.Colour.red()
        elif average_ping >= 200:
            color = nextcord.Colour.orange()
        else:
            color = nextcord.Colour.green()
        e = nextcord.Embed(color=color, title="Shard Pings", description="\n".join(description))
        e.set_footer(text=f"Average: {round(average_ping, 2)}ms")
        await ctx.send(embed=e)
        
def setup(bot):
    bot.add_cog(Info(bot))