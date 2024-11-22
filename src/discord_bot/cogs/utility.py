# -*- coding: utf-8 -*-
import asyncio
import sys
import io
import base64
import discord
from discord.ext import commands
import os
import time
from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot


class Utility(commands.Cog):

    def __init__(self, bot: 'CoalitionBot'):
        self.bot = bot

    @commands.command(aliases=["latency"])
    async def ping(self, ctx: commands.Context) -> None:
        """
        Responds with 'Pong' and the latency time.
        """
        start_time = time.time()
        await ctx.message.send("Pinging...")
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        await ctx.message.edit(content=f"Pong! `{latency}ms`")

    @commands.command(aliases=["self_clear"])
    async def self_purge(self, ctx: commands.Context, limit: int) -> None:
        """
        Purges a specified number of our messages in the channel.
        """
        i = 0
        async for message in ctx.channel.history(limit=float('inf')):
            if message.author == self.bot.user:
                await message.delete()
                i += 1
                
                if i >= limit:
                    break

    @commands.command(aliases=["set_nickname", "change_nick"])
    async def edit_nickname(self, ctx: commands.Context, *, nickname: str) -> None:
        """
        Edits the nickname of the author of the message.
        """
        await ctx.author.edit(nick=nickname)

    @commands.command(aliases=["serverinfo", "guild_info"])
    async def server_info(self, ctx: commands.Context) -> None:
        """
        Displays server information in a normal text format.
        """
        guild = ctx.guild
        guild_info = (
            f"**Server Info for {guild.name}**\n"
            f"------------------------------\n"
            f"**Server ID**      : `{guild.id}`\n"
            f"**Owner**          : {guild.owner}\n"
            f"**Member Count**   : `{guild.member_count}`\n"
            f"**Roles**          : `{len(guild.roles)}`\n"
            f"**Text Channels**  : `{len(guild.text_channels)}`\n"
            f"**Voice Channels** : `{len(guild.voice_channels)}`\n"
            f"**Categories**     : `{len(guild.categories)}`\n"
        )

        # Include a clickable server icon link if available
        if guild.icon:
            icon_url = f"[Click here to view the server icon]({guild.icon.url})"
        else:
            icon_url = "No server icon available."

        # Send the guild info in a clean, markdown formatted message
        await ctx.message.edit(f"{guild_info}\n{icon_url}")
        
    @commands.command(aliases=["inv_info", "inviteinfo", "iinfo"])
    async def invite_info(self, ctx: commands.Context, code: discord.Invite) -> None:
        """
        Provides information about a given Discord invite code.
        """
        inviter = code.inviter if code.inviter else "Unknown"
        guild = code.guild if code.guild else "Unknown"
        channel = code.channel if code.channel else "Unknown"

        info_message = (
            f"**Invite Information:**\n"
            f"-----------------------\n"
            f"**Inviter**  : {inviter}\n"
            f"**Guild**    : {guild}\n"
            f"**Channel**  : {channel}\n"
        )

        await ctx.reply(info_message)
    
    @commands.command(aliases=['makeguild', 'createaguild', 'createserver', 'createguild', 'create_server'])
    async def create_guild(self, ctx: commands.Context, name: str):
        '''
        Creates a guild.
        '''
        resp = await self.bot.create_request(method='POST', url='https://discordapp.com/api/v9/guilds', headers={'Authorization': os.getenv('DISCORD_TOKEN'), 'x-debug-options': 'bugReporterEnabled', 'x-discord-locale': 'en-US', 'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJjYW5hcnkiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC43MTMiLCJvc192ZXJzaW9uIjoiMTAuMC4xOTA0NSIsIm9zX2FyY2giOiJ4NjQiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoxOTA0NTIsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjMxNDU5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9'}, json={'name': name})
        await ctx.send(f'Successfully Created [Guild](https://discord.com/channels/{resp["json"]["id"]})')
    
    @commands.command(aliases=['newprefix', 'makeprefix', 'addprefix'])
    async def add_prefix(self, ctx: commands.Context, *, prefix: str):
        '''
        Adds a prefix for command context.
        '''
        self.bot.prefixes.append(prefix)
        if prefix in self.bot.prefixes:
            await ctx.send(f'Successfully added prefix: "{prefix}"')
    
    @commands.command(aliases=['showprefixes', 'show_prefixes', 'getprefixes'])
    async def get_prefixes(self, ctx: commands.Context):
        '''
        Sends all of the currently set prefixes.
        '''
        await ctx.send(self.bot.prefixes)
    
    @commands.command(aliases=['stream'])
    async def streaming(self, ctx: commands.Context, url: str, *, name):
        '''
        Sets presence to Streaming.
        '''
        await self.bot.change_presence(activity=discord.Streaming(name=name, url=url))
        await ctx.send('Successfully set presence to: Streaming')
    
    @commands.command(aliases=['watch'])
    async def watching(self, ctx: commands.Context, *, name):
        '''
        Sets presence to Watching.
        '''
        await self.bot.change_presence(activity=discord.Activity(type=3, name=name))
        await ctx.send('Successfully set presence to: Watching')
    
    @commands.command(aliases=['listen'])
    async def listening(self, ctx: commands.Context, *, name):
        '''
        Sets presence to Listening
        '''
        await self.bot.change_presence(activity=discord.Activity(type=2, name=name))
        await ctx.send('Successfully set presence to: Listening')
    
    @commands.command(aliases=['play'])
    async def playing(self, ctx: commands.Context, *, name):
        '''
        Sets presence to Playing.
        '''
        await self.bot.change_presence(activity=discord.Activity(type=0, name=name))
        await ctx.send('Successfully set presence to: Playing')
    
    @commands.command(aliases=['compete'])
    async def competing(self, ctx: commands.Context, *, name):
        '''
        Sets presence to Competing.
        '''
        await self.bot.change_presence(activity=discord.Activity(type=5, name=name))
        await ctx.send('Successfully set presence to: Competing')
    
    @commands.command(aliases=['deletepresence', 'delete_presence', 'removepresence'])
    async def remove_presence(self, ctx: commands.Context):
        '''
        Removes a presence (not status presence).
        '''
        await self.bot.change_presence(activity=discord.Activity(type=-1, name=''))
        await ctx.send('Successfully removed presence')

    @commands.command()
    async def online(self, ctx: commands.Context):
        '''
        Sets presence to Online.
        '''
        await self.bot.change_presence(status='online')
        await ctx.send('Successfully set status to: Online')

    @commands.command(aliases=['idling'])
    async def idle(self, ctx: commands.Context):
        '''
        Sets presence to Idle.
        '''
        await self.bot.change_presence(status='idle')
        await ctx.send('Successfully set status to: Idle')
    
    @commands.command(aliases=['dnd', 'donotdisturb'])
    async def do_not_disturb(self, ctx: commands.Context):
        '''
        Sets presence to Do Not Disturb.
        '''
        await self.bot.change_presence(status='dnd')
        await ctx.send('Successfully set status to: Do Not Disturb')
    
    @commands.command(aliases=['invis', 'invisible'])
    async def offline(self, ctx: commands.Context):
        '''
        Sets presence to Invisible.
        '''
        await self.bot.change_presence(status='invisible')
        await ctx.send('Successfully set status to: Invisible')
    
    @commands.command(aliases=['minfo', 'memberinfo'])
    async def member_info(self, ctx: commands.Context, member: discord.Member):
        '''
        Gets information from a member profile (member class).
        '''
        roles = []
        [roles.append(role.name) for role in member.roles]
        await ctx.send(f'''
```
Name: {member.display_name}
Is On Mobile: {member.is_on_mobile()}
Activity: {member.activity}
Joined At: {member.joined_at}
Nickname: {member.nick}
Raw Client Status: {member._client_status}
```
# Roles
```
{roles}
```
# Guild Permissions
```
{member.guild_permissions}
```
''')
    
    @commands.command(aliases=['accountinfo', 'uinfo', 'userinfo', 'whois'])
    async def user_info(self, ctx: commands.Context, user: discord.User):
        '''
        Gets information from a user profile (user class).
        '''
        space = """
"""
        if user.id == CoalitionBot.user.id:
            pfp = await self.bot.create_request(method='GET', url=str(user.avatar_url))['read']
            with io.BytesIO(pfp) as _pfp:
                await ctx.send(f"""
# Account Information
```
Name: {user.name}
ID: {user.id}
Date Created: {user.created_at.strftime("%A, %d %B %Y %I:%M %p")}
Part of Token: {str(base64.b64encode(f"{user.id}".encode("utf-8")), "utf-8").replace('==', '')}
```
""", file=discord.File(_pfp, 'pfp.png'))
        else:
            mutual_guilds = []
            [mutual_guilds.append(guild.name) for guild in user.mutual_guilds]
            pfp = await self.bot.create_request(method='GET', url=str(user.avatar_url))['read']
            with io.BytesIO(pfp) as _pfp:
                await ctx.send(f"""
# Account Information
```
Name: {user.name}
ID: {user.id}
Date Created: {user.created_at.strftime("%A, %d %B %Y %I:%M %p")}
Part of Token: {str(base64.b64encode(f"{user.id}".encode("utf-8")), "utf-8").replace('==', '')}
```
# Mutual Guilds
```
{str(mutual_guilds).replace("'", "").replace("[", "").replace("]", "").replace(",", space)}
```""", file=discord.File(_pfp, 'pfp.png'))
    
    @commands.command(aliases=['exitguild', 'exit_guild', 'deleteguild', 'delete_guild', 'leaveguild'])
    async def leave_guild(self, ctx: commands.Context):
        '''
        Leaves/Deletes (only if permissible) the guild that the command is ran in.
        '''
        try:
            await ctx.guild.delete()
        except discord.errors.Forbidden:
            await ctx.guild.leave()
    
    @commands.command(aliases=['makechannel', 'makech', 'createch', 'createchannel'])
    async def create_text_channel(self, ctx: commands.Context, *, name):
        '''
        Creates a text channel.
        '''
        await ctx.guild.create_text_channel(name)
        await ctx.send(f'Successfully created text channel with name: {name}')

    @commands.command(aliases=['makecategory'])
    async def create_category(self, ctx: commands.Context, *, name):
        '''
        Creates a category.
        '''
        await ctx.guild.create_category(name)
        await ctx.send(f'Successfully created category with name: {name}')
    
    @commands.command(aliases=['makevoice', 'makevc', 'createvc'])
    async def create_voice_channel(self, ctx: commands.Context, *, name):
        '''
        Creates a voice channel.
        '''
        await ctx.guild.create_voice_channel(name)
        await ctx.send(f'Successfully created voice channel with name: {name}')
    
    @commands.command(aliases=['makerole'])
    async def create_role(self, ctx: commands.Context, *, name):
        '''
        Creates a role.
        '''
        await ctx.guild.create_role(name)
        await ctx.send(f'Successfully created role with name: {name}')
    
    @commands.command(aliases=['editguild', 'guildname'])
    async def change_guild_name(self, ctx: commands.Context, *, name):
        """
        Changes a guild's name
        """
        await ctx.guild.edit(name=name)
        await ctx.send(f'Successfully changed guild name to: {name}')
    
    @commands.command(aliases=["mark_all", "read_all", "mark_read", "read_guilds"])
    async def ack(self, ctx: commands.Context, fast=False) -> None:
        """
        Marks all guilds as read for the bot.
        """
        await ctx.message.edit("Marking all guilds as read...")
        
        if fast:
            tasks = [asyncio.create_task(guild.ack()) for guild in self.bot.guilds]
            for task in asyncio.as_completed(tasks):
                task = await task
                print(f"Marked guild as read.")
        else:
            for guild in self.bot.guilds:
                await guild.ack()
                print(f"Marked guild as read.")
        await ctx.reply("All guilds have been marked as read.")

    @commands.command(aliases=["reboot", "restartbot"])
    async def restart(self, ctx: commands.Context) -> None:
        """
        Restarts the bot.
        """
        await ctx.message.edit("Restarting bot...")
        os.execv(sys.executable, ['python'] + sys.argv)


    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        """
        Listens to any command issued by the user and stores it as the last command.
        """
        
        # do not count "repeat" and "editrepeat" commands
        if ctx.command and ctx.command.name in ['repeat', 'editrepeat']:
            return
        
        # Store the full command (name + arguments) in the last_command variable
        self.last_command = ctx.message.content

    @commands.command(name="repeat", aliases=['r'])
    async def repeat_last_command(self, ctx: commands.Context) -> None:
        """
        Repeats the last command issued by the user.
        """
        if not self.last_command:
            await ctx.message.edit("No command to repeat!")
            return
        
        ctx.message.content = self.last_command
        
        # await ctx.message.delete()
        
        # Send the last command as if the user just issued it
        # await ctx.send(self.last_command)
        await self.bot.process_commands(ctx.message)
        
        # # Simulate the last command execution
        # await ctx.invoke(self.bot.get_command(self.last_command.split()[0]), *self.last_command.split()[1:])
    

    @commands.command(name='editrepeat', aliases=['edit_repeat', 'er'])
    async def edit_repeat(self, ctx: commands.Context) -> None:
        """
        Repeats the last command issued by the user, AFTER the message has been edited.
        """
        if not self.last_command:
            await ctx.message.edit("No command to edit!")
            return
        
        PREFIX = '`EDIT COMMAND BELOW`:\n'
        if len(self.last_command) > 2000 - len(PREFIX):
            await ctx.message.edit("Command too long to edit safely.")
            return
            
        await ctx.message.delete()
        
        content = f"{PREFIX}{self.last_command[:1990]}"

        # send message to be edited.
        await ctx.send(content)
        
        # now wait for an edit on said message.
        def check(old: discord.Message, new: discord.Message) -> bool:
            return old.author == ctx.author and old.channel == ctx.channel
        
        try:
            old, new = await self.bot.wait_for('message_edit', check=check, timeout=60)
            actual_content = new.content.replace(PREFIX, '')
            new.content = actual_content
            await self.bot.process_commands(new)
        except asyncio.TimeoutError:
            await ctx.message.edit("Edit timed out. Rejecting edit.")
            return


async def setup(bot: commands.Bot) -> None:
    """
    Adds the Utility cog to the bot.
    """
    await bot.add_cog(Utility(bot))
