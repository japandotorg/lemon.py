import sys

cog = sys.argv[1]
file = cog.lower()

script = f"""import discord
from discord.ext import commands
from bot import core
__all__ = ("setup",)
class {cog}(commands.Cog):
    def __init__(self, bot: core.CustomBot):
        self.bot = bot
def setup(bot: core.CustomBot):
    bot.add_cog({cog}(bot))
"""

with open(f"./cogs/{file}.py", "w") as f:
    f.write(script)

print(f"Created cog at ./cogs/{file}.py")