#!/usr/bin/env python

import logging
from asyncio import AbstractEventLoop, Event
from collections import Counter, deque
from random import SystemRandom
from statistics import mean
from typing import List, Union

import nextcord
from aiohttp import ClientSession
from nextcord.ext import commands

import config
from web import ipc

log = logging.getLogger("nextcord.example")
logging.basicConfig(level=logging.INFO)

__all__ = ("nextcord.example")

@ipc.route(name="test")
async def test(text):
    return "this is a cool thing: {}".format(
        text
    )
    
@ipc.route(name="stats")
async def cool(bot):
    return {
        "users": format(sum(1 for i in bot.users if not i.bot), ","),
        "guilds": format(len(bot.guilds), ","),
    }
    
def get_prefix(bot: "nextcord.example", message: nextcord.Message) -> Union[List[str], str]:
    return commands.when_mentioned_or(*config.prefix)(bot, message)

class Extra:
    def __init__(self):
        self.message_latencies = deque(maxlen=500)
        self.socket_stats = Counter()
        self.commands_stats = Counter()
        
    @property
    def message_latency(self):
        return 1000 * mean(lat.total_seconds() for lat in self.message_latencies)
    
class NextcordExample(commands.Bot):
    loop: AbstractEventLoop
    
    def __init__(self, loop: AbstractEventLoop) -> None:
        intents = nextcord.Intents.default()
        intents.members = True
        super().__init__(
            command_prefix=get_prefix,
            skip_after_prefix=True,
            case_insensitive=True,
            intents=intents,
            max_messages=750,
            owner_id=759180080328081450,
            loop=loop,
        )
        
        self.__BotBase__cogs = commands.core._CaseInsensitiveDict()
        
        self.loop.create_task(self.__prep())
        self.prepped = Event()
        
        self.random = SystemRandom()
        self.extra = Extra()
        self.start_time = None
        
        self.context = commands.Context
        
    async def __prep(self):
        self.session = ClientSession(
            headers={"User-Agent": "japandotorg (https://github.com/japandotorg/lemon.py)"}
        )
        await self.wait_until_ready()
        async with self.pool.acquire() as conn:
            await conn.executemany(
                "INSERT INTO public.guilds (id) VALUES ($1) ON CONFLICT DO NOTHING",
                tuple((g.id) for g in self.guilds),
            )
        self.prepped.set()
        log.info("Completed preparation...")
        
    def load_extension(self):
        extensions = [
            "core.context",
            "cogs.actions",
            "cogs.info",
            "cogs.mod",
        ]
        for ext in extensions:
            self.load_extension(ext)
        self.load_extension("jishaku")
        log.info("Loaded extensions...")
        
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or self.context)
    
    async def login(self, token: str):
        await super().login(token)
        self.start_time = nextcord.utils.utcnow()
        
    def run(self, *args, **kwargs):
        self.load_extensions()
        super().run(*args, **kwargs)
        
    async def close(self):
        await self.session.close()
        await self.pool.close()
        await super().close()
        
    async def on_ready(self):
        log.info("Connected to Discord...")
        
    @staticmethod
    def embed(**kwargs):
        color = kwargs.pop("color", nextcord.Color.blurple())
        return nextcord.Embed(**kwargs, color=color)
    
    async def paste(self, data: str, url="https://sourceb.in"):
        async with self.session.post(url + "/documents", data=bytes(str(data), "utf-8")) as r:
            res = await r.json()
        key = res["key"]
        return url + f"/{key}"
    
    async def getch_user(self, user_id: int) -> nextcord.User:
        user = self.get_user(user_id)
        if user is None:
            user = await self.fetch_user(user_id)
        return user