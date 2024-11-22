# -*- coding: utf-8 -*-
import asyncio
from discord.ext import commands
import time
from selenium import webdriver

from src.utils import userid_from_token
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot


class ClientSided(commands.Cog):
    
    def __init__(self, bot: 'CoalitionBot'):
        self.bot = bot
        self.running_drivers: list[webdriver.Chrome] = []
        
        
    def login_to_token(self, token: str):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        self.running_drivers.append(driver)
        driver.get("https://discord.com/login")
        driver.execute_script(
            """function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}"""
            + f'\nlogin("{token}")'
        )
        
        # halt util "login" is no longer in url
        while "login" in driver.current_url:
            time.sleep(0.5)
        
        
    @commands.command(aliases=["tlogin"])
    async def tokenlogin(self, ctx: commands.Context, token: str):
        """
        Logs in to Discord via the browser using a token.
        """
        await ctx.message.edit(content=f"Attempting to log into id {userid_from_token(token)} with token...")
        await self.bot.loop.run_in_executor(self.bot.threadpool, self.login_to_token, token)
        await ctx.message.edit(content=f"Logged into user id: {userid_from_token(token)}.")

    
    @commands.command(aliases=["tlogout"])
    async def tokenlogout(self, ctx: commands.Context):
        """
        Logs out of Discord via the browser.
        """
        await ctx.message.edit(content="Logging out...")
        driver_len = len(self.running_drivers)
        for driver in self.running_drivers:
            driver.quit()
        self.running_drivers.clear()
        await ctx.message.edit(content=f"Logged out of {driver_len} tokens.")

async def setup(bot: commands.Bot) -> None:
    """
    Adds the Utility cog to the bot.
    """
    await bot.add_cog(ClientSided(bot))
