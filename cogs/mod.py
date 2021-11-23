import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions
from nextcord.errors import Forbidden

class Moderation(commands.Cog):
    """
    Moderation Commands for admins/mods
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('\`Moderation\` has been loaded')
        
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
                await ctx.send(f'User {user.mention} has been unbanned')
                return
            
    @commands.command()
    @has_permissions(administrator=True)
    async def lockdown(self, ctx, role : commands.RoleConverter):
        role = ctx.guild.roles[1]
        perms = nextcord.Permissions(view_channel=False)
        await role.edit(permissions=perms)
        await ctx.send('Server locked')
        
    @commands.command()
    @has_permissions(administrator=True)
    async def unlockdown(self, ctx, role : commands.RoleConverter):
        role = ctx.guild.roles[1]
        perms = nextcord.Permissions(view_channel=True)
        await role.edit(permissions=perms)
        await ctx.send('Server unlocked')
        
def setup(bot):
    bot.add_cog(Moderation(bot))