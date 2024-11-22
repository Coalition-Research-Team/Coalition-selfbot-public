from concurrent.futures import ThreadPoolExecutor
from typing import Any
import aiohttp
from discord import Message
import discord
from discord.ext import commands
import asyncio
import os

from .cogs.moderation import Moderation
from .cogs.utility import Utility
from .cogs.webhooks import Webhook
from .cogs.destruction import Destruction
from .cogs.client_sided import ClientSided
from .cogs.admin import Admin
from .cogs.proxies import Proxies

# Request Construction
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s | %(message)s')

class Construction:

    def __init__(self):
        self.success_codes = (200, 201, 202, 203, 204, 205)
    
    @classmethod
    def log(self, level, msg: str):
        return logging.log(level=level, msg=msg)

# Bot Setup
class CoalitionBot(commands.Bot, Construction):

    def __init__(self, prefixes: list, *args, **kwargs):
        commands.Bot.__init__(self, command_prefix=prefixes, *args, **kwargs)
        Construction.__init__(self)  # Initialize `Construction` to set `success_codes`
        self.prefixes = prefixes
        self.threadpool = ThreadPoolExecutor()
        
        self.proxy = kwargs.get('proxy')
   
 
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
    
    async def on_command_error(self, ctx: commands.Context, error):
        await ctx.reply(f'Command "{ctx.command.name} failed, forwarding error...')
        await ctx.send(f'Type: {type(error)} | Description: `{error}`')
        await super().on_command_error(ctx, error)
    
    async def create_request(self, method: str, url: str, headers: dict = None, json: dict = None):
        
        async with self.session.request(method=method, url=url, headers=headers, json=json) as resp:
            if resp.status in self.success_codes:
                self.log(logging.INFO, f'Received response of {resp.status}')
            else:
                self.log(logging.WARNING, f'Received abnormal response of {resp.status}')
            if 'retry_after' in str(await resp.json()):
                await asyncio.sleep((await resp.json())['retry_after'])
            return {'text': await resp.text(), 'json': await resp.json(), 'read': await resp.content.read()}
 
    async def close(self) -> None:
        await self.session.close()
        self.threadpool.shutdown(wait=True)
        return await super().close()
        

    async def setup_hook(self):
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5000))
        await self.add_cog(Moderation(self))
        await self.add_cog(Utility(self))
        await self.add_cog(Webhook(self))
        await self.add_cog(Destruction(self))
        await self.add_cog(ClientSided(self))
        await self.add_cog(Admin(self))
        await self.add_cog(Proxies(self))
    