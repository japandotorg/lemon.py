#!/usr/bin/env python

import os
import tomlkit
import logging
import nextcord

from pathlib import Path
from nextcord.ext.tasks import loop
from database import database as botdb
from nextcord.ext import commands, tasks

config_file = Path("config.toml")

if not config_file.is_file():
    raise FileNotFoundError(
        "Cannot find the config file"
    )
    
bot_config = tomlkit.parse(config_file.read_text())

if os.environ.get("MY_DATABAsE"):
    bot_config["bot"]["database"] = os.environ.get("MY_DATABASE")

logger = logging.getLogger("nextcord")
logger.setLevel(bot_config["bot"]["logging_level"])
handler = logging.FileHandler(filename="nextcord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

myIntents = nextcord.Intents.all()

description = "nextcord template bot"

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*bot_config["bot"]["prefixes"]),
    description=description,
    case_insensitive=True,
    allowed_mentions=nextcord.AllowedMentions(
        everyone=False,
        users=False,
        roles=False
    ),
    intents = myIntents
)
bot.remove_command('help')

@tasks.loop(seconds=10.0)
@bot.event
async def on_connect():
    await bot.change_presence(
        status=nextcord.Status.idle,
        activity=nextcord.Game(
            name="Starting up..."
        )
    )
    
@bot.event
async def on_disconnect():
    for cog in bot.cogs:
        bot.remove_cog(cog[0])
        
@bot.event
async def on_ready():
    print("[ {bot.user.name} ] Logged into discord...")
    
    logger.log(logging.INFO, f"Logged in as {bot.user.name} [ {bot.user.id} ]")
    
    activity = "{}help".format(bot_config["bot"]["prefixes"][0])
    
    await bot.change_presence(
        status=nextcord.Status.online,
        activity=nextcord.game(name=activity)
    )
    
    global loaded_cogs
    global conn
    conn = await botdb.init_dbconn(bot_config["bot"]["database"])
    
    logger.log(logging.INFO, f"{bot.user.name} Ready")
    
@bot.command()
async def load(ctx, extension):
    if (ctx.messsage.author.permissions_in(ctx.message.channel).manage_messages):
        bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'Loaded cog `{extension}')
        
@bot.command()
async def unload(ctx, extension):
    if (ctx.message.author.permissions_in(ctx.message.channel).manage_messages):
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Unloaded cog `{extension}')
        
for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        
bot.run(bot_config["bot"]["token"])