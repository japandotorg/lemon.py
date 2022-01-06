import re
import math
import json
import typing
import logging
import datetime

import nextcord
from nextcord.errors import Forbidden
from nextcord.ext import commands, tasks
from nextcord.ext.commands import has_permissions

time_match = re.compile(
    r"((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?"
)

def none_to_zone(arg):
    if arg is None:
        return 0
    else:
        return arg
    
def get_timedelta_from_string(time_string: str) -> datetime.timedelta:
    result = time_match.match(time_string)
    time = [
        result.group("weeks"),
        result.group("days"),
        result.group("hours"),
        result.group("minutes"),
    ]
    time = [int(none_to_zone(y)) for y in time]
    
    time_obj = datetime.timedelta(
        weeks=time[0],
        days=time[1],
        hours=time[2],
        minutes=time[3]
    )
    return time_obj

class Duration(commands.Converter):
    async def convert(self, ctx, argument):
        return get_timedelta_from_string(argument)

class Moderation(commands.Cog):
    """
    Moderation Commands for admins/mods
    """
    
    def __init__(self, bot, conn, bot_config, logger):
        self.bot = bot
        self.conn = conn
        self.bot_config = bot_config
        self.logger = logger
        self.logger.log(logging.INFO, "Loaded moderation cog")
        print("Loaded moderation cog")
        self.do_pending_actions.start()
        
    def cog_unload(self):
        self.do_pending_actions.cancel()
        
    @tasks.loop(seconds=30.0)
    async def do_pending_actions(self):
        guild = self.bot.get_guild(self.bot_config["guild"]["guild_id"])
        actions = await self.conn.get_pending_actions()
        for action in actions:
            if action[4] < datetime.datetime.utcnow():
                member = guild.get_member(action[5])
                if (
                    action[1] == "mute"
                    or action[1] == "hardmute"
                    or action[1] == "glitch"
                ):
                    await self.unmute_inner(member, action[2], action[3])
                    await self.conn.add_to_mod_logs(
                        member.id,
                        self.bot.user.id,
                        "unmute",
                        "Automatic unmute"
                    )
                    await self.make_log_embed(
                        member,
                        "unmuted",
                        guild.get_member(self.bot.user.id),
                        "Automatic unmute",
                    )
                    await self.conn.delete_pending_actions(action[0])
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('\`Moderation\` has been loaded')
        
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: nextcord.Member, *, reason: str):
        if member.id == self.bot.user.id:
            await ctx.send(f"You cannot warn yourself")
            return True
        await ctx.trigger_typing()
        await self.conn.add_to_mod_logs(
            member.id,
            ctx.author.id,
            "warn",
            reason
        )
        await member.send(f"You were warned in {ctx.guild.name}. Reason: {reason}")
        await self.make_log_embed(
            member,
            "warned",
            ctx.author,
            reason
        )
        await ctx.send(f"Warned  **{member}**")    
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, user: commands.MemberConverter, *, message: str):
        """ DM the user you want to """
        try:
            await user.send(message)
            await ctx.send(f'Successfully sent a DM to **{user}**')
        except nextcord.Forbidden:
            await ctx.send('This user have their DM\'s locked')
            
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter):
        """ Kicks the specified member """
        await ctx.send('Please specify the reason!')
        msg = await self.bot.wait_for('message')
        reason = msg.content
        description = f'''
        **Member:** = {member}
        **Responsible moderator:** {ctx.author.mention}
        **Reason:** {reason}
        '''
        
        embed = nextcord.Embed(
            title='kick',
            description=description,
            colour=nextcord.Colour.green()
        )
        try:
            await member.kick(reason=reason)
            await ctx.send(
                content=None,
                embed=embed
            )
        except Forbidden:
            try:
                await ctx.send('I don\'t have enough permissions to kick the person')
            except Forbidden:
                await ctx.author.send(
                    f'Hey, I don\'t have enough permissions to send messages in{ctx.channel.name} on {ctx.guild.name}\n',
                    embed=embed
                )
                
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter):
        """ Bans the specified member """
        await ctx.send('Please specify the reason!')
        msg = await self.bot.wait_for('message')
        reason = msg.content
        description = f'''
        **Member:** = {member}
        **Responsible moderator:** {ctx.author.mention}
        **Reason:** {reason}
        '''
        
        embed = nextcord.Embed(
            title='Ban',
            description=description,
            colour=nextcord.Colour.green()
        )
        embed.set_image(
            url='https://media.giphy.com/media/yIdJwdk14j39Lm3epL/giphy.gif'
        )
        try:
            await member.ban(reason=reason)
            await ctx.send(
                content=None,
                embed=embed
            )
        except Forbidden:
            try:
                await ctx.send('I don\'t have enough permissions to kick the person')
            except Forbidden:
                await ctx.author.send(
                    f'Hey, I don\'t have enough permissions to send messages in{ctx.channel.name} on {ctx.guild.name}\n',
                    embed=embed
                )
                
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        
        for ban_entry in banned_users:
            user = ban_entry.user
            
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.trigger_typing()
                await ctx.send(f'User {user.mention} has been unbanned')
                return
            
    @commands.command()
    @has_permissions(ban_members=True, manage_guild=True)
    async def massban(self, ctx, users: commands.Greedy[nextcord.User]):
        await ctx.trigger_typing()
        for user in users:
            await ctx.guild.ban(
                user,
                reason=f"Massban initiated by {str(ctx.author)}"
            )
        await ctx.send(f"Banned {len(users)} users")
            
    @commands.command()
    @has_permissions(administrator=True)
    async def lockdown(self, ctx, role : commands.RoleConverter):
        role = ctx.guild.roles[1]
        perms = nextcord.Permissions(view_channel=False)
        await role.edit(permissions=perms)
        await ctx.trigger_typing()
        await ctx.send('Server locked')
        
    @commands.command()
    @has_permissions(administrator=True)
    async def unlockdown(self, ctx, role : commands.RoleConverter):
        role = ctx.guild.roles[1]
        perms = nextcord.Permissions(view_channel=True)
        await role.edit(permissions=perms)
        await ctx.trigger_typing()
        await ctx.send('Server unlocked')
        
    @commands.command()
    @has_permissions(manage_messages=True)
    async def modlog(
        self,
        ctx,
        user: nextcord.User,
        page: typing.Optional[int] = 1,
    ):
        await ctx.trigger_typing()
        mod_logs = await self.conn.get_logs_for_user(user.id)
        mod_logs.reverse()
        minimum = (page - 1) * 10
        maximum = page * 10
        if len(mod_logs) < minimum:
            await ctx.send("That page doesn't exist")
            return True
        if len(mod_logs) <= maximum:
            maximum = len(mod_logs)
        mod_log_page = mod_logs[minimum:maximum]
        embed = nextcord.Embed(
            colour=nextcord.Colour.green(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_author(
            name=str(user),
            icon_url=str(user.avatar_url)
        )
        embed.set_footer(
            text=f"ID: {user.id}"
        )
        for log_entry in mod_log_page:
            embed = await self.add_log_entry(embed, log_entry)
        if mod_logs:
            embed.title = f"Page {page}/{math.ceil(len(mod_logs) / 10)}"
        else:
            embed.description = "There are no moderation logs for this user"
        await ctx.send(embed=embed)
        
    @modlog.error
    async def modlogs_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"```{ctx.prefix}modlogs <user: User> [page: int]```\nError: missing required parameter `{error.param.name}`"
            )
        
    async def add_log_entry(
        self,
        embed: nextcord.Embed,
        entry: list,
    ) -> nextcord.Embed:
        mod = self.bot.get_user((entry[2]))
        embed.add_field(
            name=f"Case #{entry[0]}: {entry[3]}",
            value=f"By **{mod}** ({entry[2]})\nReason: **{entry[4]}**\nTime: {entry[5].strftime('%Y-%m-%d %H:%M:%S')} UTC",
            inline=False,
        )
        return embed
    
    @commands.command()
    @has_permissions(manage_messages=True)
    async def glitch(
        self,
        ctx,
        member: nextcord.Member,
        duration: Duration,
        *,
        reason: typing.Optional[str] = None,
    ):
        mute_role = ctx.guild.get_role(self.bot_config["mod"]["glitch_role"])
        if member.top_role.position >= ctx.author.top_role.position:
            await ctx.send("You are not high enough in the role heirarchy to do that")
            return True
        if mute_role in member.roles:
            await ctx.send(f'{member} is already glitched')
            return True
        await ctx.trigger_typing()
        if not reason:
            reason = "No reason specified"
        expire_time = datetime.datetime.utcnow() + duration
        await self.conn.set_pending_action(
            member.id,
            "glitch",
            [mute_role.id],
            None,
            expire_time,
        )
        await member.add_roles(mute_role)
        await self.conn.add_to_mod_logs(member.id, ctx.author,id, "glitch", reason)
        await ctx.send(
            f"**{ctx.message.author}** glitched **{member}** for {duration}. Reason: {reason}"
        )
        await member.send(
            f"You were glitchd in {ctx.guild.name} for {duration}. Reason: {reason}"
        )
        await self.make_log_embed(member, "glitched", ctx.author, reason)
        
    @glitch.error
    async def glitch_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"```{ctx.prefix}glitch <@user/ID> <time> [reason]```\nError: missing required parameter `{error.param.name}`"
            )
            
    @commands.command()
    @has_permissions(manage_guild=True)
    async def export(self, ctx):
        await ctx.trigger_typing()
        data = await self.conn.export_all()
        users = {}
        json_export = {
            "requester": str(ctx.message.author.id),
            "timestamp": str(datetime.datetime.utcnow()),
            "actions": [],
        }
        for action in data:
            if action[1] in users:
                user = users[action[1]]
            else:
                user = self.bot.get_user(action[1])
                users[action[1]] = user
            if action[2] in users:
                mod = users[action[2]]
            else:
                mod = self.bot.get_user(action[2])
                users[action[2]] = mod
            action_json = {
                "id": str(action[0]),
                "user": {
                    "id": str(action[1]),
                    "username": str(user)
                },
                "mod": {
                    "id": str(action[2]),
                    "username": str(mod)
                },
                "type": action[3],
                "reason": action[4],
                "timestamp": str(action[5]),
            }
            json_export["actions"].appned(action_json)
        dump = json.dumps(json_export, indent=2)
        export_file = io.BytesIO(bytes(dump, "utf-8"))
        await ctx.send(
            content="exported file",
            file=nextcord.File(
                export_file,
                filename="export.json",
            ),
        )
    
def setup(bot):
    bot.add_cog(Moderation(bot))