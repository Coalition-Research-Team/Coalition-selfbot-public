# -*- coding: utf-8 -*-
from discord.ext import commands
from colorama import Fore as C
import colorama
from datetime import timedelta
import discord
from typing import Union
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot



class Moderation(commands.Cog):
    
    def __init__(self, bot: 'CoalitionBot'):
        self.presences = [discord.Status.dnd, discord.Status.online, discord.Status.do_not_disturb, discord.Status.idle]
        self.bot = bot

    @commands.command(aliases=["ban_user"])
    async def ban(self, ctx: commands.Context, user: discord.User) -> None:
        """
        Bans a user from the guild.
        """
        await ctx.guild.ban(user)
        await ctx.send(f"User {user} has been banned.")

    @commands.command(aliases=["kick_user"])
    async def kick(self, ctx: commands.Context, user: discord.User) -> None:
        """
        Kicks a user from the guild.
        """
        await ctx.guild.kick(user)
        await ctx.send(f"User {user} has been kicked.")

    @commands.command()
    async def purge(self, ctx: commands.Context, amount: int = 100) -> None:
        """
        Deletes a specified number of messages from the channel.
        """
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Purged {amount} messages.")
    
    @commands.command(aliases=['targetpurge'])
    async def target_purge(self, ctx: commands.Context, user: discord.User):
        '''
        Deletes all the messages of a specific user.
        '''
        try:
            for message in await ctx.channel.history(limit=float('inf')).flatten():
                if message.author.id == user.id:
                    await message.delete()
        except discord.errors.HTTPException:
            pass

    @commands.command()
    async def add_role(self, ctx: commands.Context, member: discord.Member, role: discord.Role) -> None:
        """
        Adds a role to a member.
        """
        await member.add_roles(role)
        await ctx.send(f"Role {role.name} added to {member.display_name}.")

    @commands.command()
    async def remove_role(self, ctx: commands.Context, member: discord.Member, role: discord.Role) -> None:
        """
        Removes a role from a member.
        """
        await member.remove_roles(role)
        await ctx.send(f"Role {role.name} removed from {member.display_name}.")

    @commands.command(aliases=["lock_channel"])
    async def lock(self, ctx: commands.Context, role: discord.Role) -> None:
        """
        Locks the channel, preventing the specified role from sending messages.
        """
        await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.send(f"Locked the channel for {role.name}.")

    @commands.command(aliases=["unlock_channel"])
    async def unlock(self, ctx: commands.Context, role: discord.Role) -> None:
        """
        Unlocks the channel, allowing the specified role to send messages.
        """
        await ctx.channel.set_permissions(role, send_messages=True)
        await ctx.send(f"Unlocked the channel for {role.name}.")
    
    @commands.command(aliases=['remove_everyone'])
    async def remove_everyone_permissions(self, ctx: commands.Context):
        '''
        Locks down all channels in a guild.
        '''
        await ctx.message.delete()
        failed_hides = []
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, read_messages=False)
                print(f"{C.GREEN}Hid {channel.name}")
            except Exception as e:
                failed_hides.append(channel.name)
                print(f"{C.RED}Failed to hide {channel.name}: {e}")
                if failed_hides:
                    await ctx.send(f"```arm\n{C.YELLOW}Failed to hide: {', '.join(failed_hides)}```", delete_after=3)
                else:
                    await ctx.send(f"```arm\n{C.GREEN}Successfully hid all text channels from @everyone.```", delete_after=3)
    
    @commands.command(aliases=['changenic'])
    async def give_nickname(self, ctx: commands.Context, member: discord.Member, *, nickname: str):
        '''
        Gives a user a nickname in a guild.
        '''
        await member.edit(nick=nickname)
        await ctx.send(f"Successfully set {member.mention}'s nickname to: {nickname}")
    
    @commands.command(aliases=['timeout', 'tm'])
    async def mute(self, ctx: commands.Context, member: discord.Member, duration_type: str, duration: int):
        '''
        Sets a timeout on a member.
        '''
        if duration_type == 'Days':
            if duration > 27:
                await ctx.send(f'{ctx.author.mention} Duration Is Too Long, You Can Only Set A Day Duration As 27 Days', ephemeral=True)
            else: 
                await member.timeout(duration=timedelta(days=duration))
                await ctx.send(f'Successfully Muted: {member.mention}', delete_after=2)
        if duration_type == 'Minutes':
            if duration > 40000:
                await ctx.send(f'{ctx.author.mention} Duration Is Too Long, You Can Only Set A Minute Duration As 40,000 Minutes', ephemeral=True)
            else:
                await member.timeout(duration=timedelta(minutes=duration))
                await ctx.send(f'Successfully Muted: {member.mention}', delete_after=2)
        if duration_type == 'Hours':
            if duration > 660:
                await ctx.send(f'{ctx.author.mention} Duration Is Too Long, You Can Only Set An Hour Duration As 660 Hours', ephemeral=True)
            else:
                await member.timeout(duration=timedelta(hours=duration))
                await ctx.send(f'Successfully Muted: {member.mention}', delete_after=2)
        if duration_type == 'Seconds':
            if duration > 2339999:
                await ctx.send(f'{ctx.author.mention} Duration Is Too Long, You Can Only Set A Second Duration As 2,339,999 Seconds', ephemeral=True)
            else:
                await member.timeout(duration=timedelta(seconds=duration))
                await ctx.send(f'Successfully Muted: {member.mention}', delete_after=2)
            
    @commands.command(aliases=['um', 'vcunmute'])
    @commands.has_permissions(mute_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        '''
        Self explanatory, removes a timeout from a member who is on timeout.
        '''
        await member.timeout(duration=None)
        await ctx.send(f'Successfully Unmuted: {member.mention}')
        
    @commands.command(aliases = ["massmute", "mm", "voicemute"])
    @commands.has_permissions(mute_members=True)
    async def massvoicemute(self, ctx: commands.Context):
        failed_channels = []
        for channel in ctx.guild.voice_channels:
            try:
                for member in channel.members:
                    await member.edit(mute=True)
            except Exception as e:
                failed_channels.append(channel.name)
                print(f"{C.RED}Failed to mute members in voice channel {channel.name}: {e}")
        if failed_channels:
                await ctx.send(f"{C.YELLOW}```arm\nFailed to mute members in voice channels: {C.RED}{', '.join(failed_channels)}```")
        else:
                await ctx.send(f"{C.GREEN}```arm\nMuted all members in voice channels.```", delete_after = 2)

    @commands.command()
    @commands.has_permissions(mute_members=True)
    async def massunmute(self, ctx: commands.Context):
        await ctx.message.delete()
        try:
            for vc in ctx.guild.voice_channels:
                for member in vc.members:
                    await member.edit(mute=False)
                    print(f"{C.GREEN}Unmuted {member.name}#{member.discriminator} in {vc.name}")
                await ctx.send(f"```arm\n{C.GREEN}Unmuted all users in voice channels.```", delete_after=3)

        except Exception as e:
                print(f"{C.RED}Failed to unmute users: {e}")
                await ctx.send(f"```arm\n{C.RED}Failed to unmute users in voice channels.```", delete_after=3)

    @commands.command(aliases=['memberonlinecount'])
    async def onlinecount(self, ctx: commands.Context):
        '''
        Checks how many members are currently online in a server.
        '''
        count = 0
        async for member in ctx.guild.fetch_members(limit = None):
            if not member.bot and member.status in self.presences:
                    count += 1
            await ctx.send(f'```arm\nThere are {count} members online in this server```')
    
    @commands.command(aliases=['softban_user'])
    async def softban(self, ctx: commands.Context, member: discord.Member):
        '''
        Bans a user and unbans them in order to delete all their messages.
        '''
        await ctx.guild.ban(user=member, delete_message_days=7)
        await ctx.guild.unban(user=member)
        await ctx.send(f'Successfully Softbanned: {member.mention}')
        
    @commands.command(aliases = ["slowmode", "sm", "slowmo", "channelslow"])
    @commands.has_permissions(manage_channels=True)
    async def massslowmode(ctx, seconds: int):
        '''
        Sets a slowmode on every channel in a guild.
        '''
        if seconds < 0:
            await ctx.send(f"```arm\n{C.RED}Slowmode cannot be negative.```", delete_after=3)
            return
        
        failed_channels = []
        
        for channel in ctx.guild.text_channels:
            
            try:
                await channel.edit(slowmode_delay=seconds)
            except Exception as e:
                failed_channels.append(channel.name)
                print(f"{C.RED}Failed to set slowmode for channel {channel.name}: {e}")
                
                if failed_channels:
                    await ctx.send(f"```arm\n{C.YELLOW}Failed to set slowmode for channels: {', '.join(failed_channels)}```", delete_after = 3)
                else:
                    await ctx.send(f"```arm\n{C.GREEN}Set slowmode to {seconds} seconds for all channels.```", delete_after = 3)
    
    @commands.command(aliases=['setslowmode'])
    async def channel_slowmode(self, ctx: commands.Context, channel: discord.TextChannel, seconds: int):
        '''
        Sets a slowmode for the "TextChannel" class. Duration type is in seconds.
        '''
        await channel.edit(slowmode_delay=seconds)
        await ctx.send(f'Successfully set a slowmode on channel: {channel.mention}')

async def setup(bot: commands.Bot) -> None:
    """
    Adds the Moderation cog to the bot.
    """
    await bot.add_cog(Moderation(bot))