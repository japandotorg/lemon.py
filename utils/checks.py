from nextcord.ext import commands

__all__ = ("can_run")

can_run = commands.bot_has_permissions

has_permissions = commands.has_permissions