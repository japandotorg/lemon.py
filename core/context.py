from nextcord.ext import commands

from . import NextcordExample

__all__ = ("NextcordExampleContext", "setup", "teardown")

class NextcordExampleContext(commands.Context):
    bot: NextcordExample
    
def setup(bot: NextcordExample) -> None:
    bot.context = NextcordExampleContext
    
def teardown(bot: NextcordExample) -> None:
    bot.context = commands.Context