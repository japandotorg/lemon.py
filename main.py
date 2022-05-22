#!/usr/bin/env python

import asyncio
import os
import logging
from asyncio import get_event_loop
from traceback import format_exc

import click
from asyncpg import Pool, create_pool

import database as db
from core import NextcordExample
from config import postgres_uri, token

log = logging.getLogger("nextcord.example.bot")

def run():
    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    os.environ["JISHAKU_HIDE"] = "True"
    os.environ["PYTHONIOENCODING"] = "UTF-8"
    
    loop = asyncio.get_event_loop()
    
    bot = NextcordExample(loop=loop)
    bot.pool = loop.run_until_complete(db.create_pool(bot=bot, dsn=postgres_uri, loop=bot.loop))
    
    bot.run(token)
    
@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(ctx):
    """
    Launches the client
    """
    if ctx.invoked_subcommand is None:
        run()
        
@main.command(short_help="initialises the databases for the bot", options_metavar="[options]")
@click.option("-s", "--show", help="show the output", is_flag=True)
@click.option("--start_bot", help="run bot after", is_flag=True)
def init(show: bool, start_bot: bool):
    _run = get_event_loop().run_until_complete
    try:
        pool: Pool = _run(create_pool(dsn=postgres_uri))
    except:
        click.echo(f"Could not create database connection.\n{format_exc()}", err=True)
        return

    files = (
        "general.sql",
        "users.sql",
        "events.sql",
        "stats.sql",
        "indexes.sql",
    )
    for file in files:
        with open(f"scripts/sql/{file}", encoding="utf8") as f:
            read = f.read()
            if show:
                print(read)
            try:
                _run(pool.execute(read))
            except Exception:
                click.echo(f"Failed on file {file}.\n{format_exc()}", err=True)
                return

    log.info("Created tables.")

    if run:
        run()


if __name__ == "__main__":
    try:
        import uvloop
    except ModuleNotFoundError:
        log.warning("uvloop is not installed")
    else:
        uvloop.install()
    main()