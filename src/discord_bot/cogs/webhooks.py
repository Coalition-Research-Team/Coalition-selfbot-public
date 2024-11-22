# -*- coding: utf-8 -*-
import aiohttp
from discord.ext import commands

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot



class Webhook(commands.Cog):
    
    def __init__(self, bot: 'CoalitionBot'):
        self.bot = bot

    @commands.command(aliases=[])
    async def send_webhook(self, ctx: commands.Context, webhook_url: str, *, content: str) -> None:
        """
        Sends a message to the specified webhook URL.
        """
        async with self.bot.create_request(method='POST', url=webhook_url, json={"content": content}) as resp:
            if resp.status == 200:
                await ctx.send("Message sent successfully.")
            else:
                await ctx.send(f"Failed to send message. Status code: {resp.status}")

    @commands.command(aliases=[])
    async def create_webhook(self, ctx: commands.Context, *, name: str) -> None:
        """
        Creates a webhook in the current channel with the specified name.
        """
        webhook = await ctx.channel.create_webhook(name=name)
        await ctx.send(f"Webhook '{name}' created. URL: {webhook.url}")

    @commands.command(aliases=[])
    async def delete_webhook(self, ctx: commands.Context, webhook_url: str) -> None:
        """
        Deletes the specified webhook using its URL.
        """
        async with self.bot.create_request(method='DELETE', url=webhook_url) as resp:
            if resp.status == 204:
                await ctx.send(f"Webhook at {webhook_url} deleted.")
            else:
                await ctx.send(f"Failed to delete webhook. Status code: {resp.status}")


async def setup(bot: commands.Bot) -> None:
    """
    Adds the Webhook cog to the bot.
    """
    await bot.add_cog(Webhook(bot))
