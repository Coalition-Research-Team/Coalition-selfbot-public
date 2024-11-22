# -*- coding: utf-8 -*-
import io
import asyncio
import re
import aiohttp
import discord
import random
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot


TEST_URL = "https://httpbin.org/ip"

class Proxies(commands.Cog):
    
    def __init__(self, bot: "CoalitionBot"):
        self.bot = bot
        
        # these lists are not great, as seen by the outputs. HTML parsing would be needed to improve these. Still, a good start.
        self.proxy_sources = [
            # "https://www.proxy-list.download/api/v1/get?type=https",
            # "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all",
            # "https://spys.me/proxy.txt",
            # "https://www.sslproxies.org/",
            # "https://www.us-proxy.org/",
            # "https://proxylist.geonode.com/api/proxy-list?limit=300&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps"
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all",
            "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=10000&country=all",
            # "https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=10000&country=all",
            # "https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=10000&country=all",
            "https://spys.me/proxy.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://free-proxy-list.net/",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
            
            
            
            "https://proxylist.geonode.com/api/proxy-list?limit=300&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps", # needs parsing
            # "https://www.webanetlabs.net/premiumproxy",
            # "https://www.proxyscan.io/download?type=http",
            # "https://www.proxyscan.io/download?type=https",
            # "https://www.proxyscan.io/download?type=socks4",
            # "https://www.proxyscan.io/download?type=socks5"
        ]
        self.proxies = []
        self.verified_proxies = []
        self.seen_origins = set()  # Track the origins of verified proxies
        self.proxy_task = None  # Track the verification task

    async def get_real_ip(self):
        """
        Get the real IP address of the machine running the bot.
        This is done by sending a request without a proxy to httpbin.org/ip.
        """
        
        try:
            async with self.bot.session.get(TEST_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    self.real_ip = data["origin"]
                    print(f"Real IP: {self.real_ip}")
                else:
                    print("Failed to retrieve real IP")
        except Exception as e:
            print(f"Error getting real IP: {e}")

    async def fetch_single_proxy_source(self, source: str):
        """
        Fetch proxies from a single source.
        """
        
        proxy_regex = re.compile(r"^(?:http:\/\/|https:\/\/)?(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}$")
        has_https = "https" in source.split("://")[1]
        print(source + " " + str(has_https))
        
        try:
            async with self.bot.session.get(source) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.splitlines()  # Return a list of proxies
                    
                    # verify proxy format via regex

                    ret = []
                    
                    for line in lines:
                        if proxy_regex.match(line):
                            clean = line.strip() 
                            ret.append(f"http{'s' if has_https else ''}://{clean}")
                    
                    print(f"Fetched {len(ret)} proxies from {source}")
                    
                    return ret
                else:
                    print(f"Failed to fetch from {source}")
                    return []
        except asyncio.TimeoutError:
            print(f"Timeout fetching from {source}")
            return []
        except Exception as e:
            print(f"Error fetching from {source}: {e}")
            return []

    async def fetch_proxies(self):
        """
        Fetch proxies from all sources concurrently and store them.
        """
        
        # Create a list of tasks for concurrent fetching
        tasks = [
            self.fetch_single_proxy_source(source) for source in self.proxy_sources
        ]

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)

        # Flatten the results and remove duplicates
        self.proxies = list(set(proxy for result in results for proxy in result))

        print(f"Fetched {len(self.proxies)} unique proxies.")

    async def verify_proxy(
        self,
        proxy: str,
        timeout: aiohttp.ClientTimeout,
        semaphore: asyncio.Semaphore,
        progress_update: list,
    ) -> None:
        """
        Verifies if the proxy works by sending a test request through it.
        Ensures that the proxy IP is different from the real IP of the machine.
        Uses a semaphore to limit concurrent verifications and updates progress.
        """
        proxy_url = f"http://{proxy}" if "://" not in proxy else proxy

        async with semaphore:  # Limit the number of concurrent requests
            try:
                async with self.bot.session.get(
                    TEST_URL, proxy=proxy_url, timeout=timeout, ssl=True
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        proxy_ip = data["origin"]
                        if proxy_ip != self.real_ip and proxy_ip not in self.seen_origins:
                            progress_update[1] += 1  # Increment verified count
                            self.verified_proxies.append(proxy)
                            self.seen_origins.add(proxy_ip)
                            # print(f"Proxy {proxy_url} is working. Proxy IP: {proxy_ip}")
                        else:
                            pass
                            # print(
                            #     f"Proxy {proxy_url} failed. Same IP as real IP: {proxy_ip}"
                            # )
            except asyncio.TimeoutError:
                # print(f"Timeout verifying proxy {proxy_url}")
                pass
            except Exception as e:
               # print(f"Error verifying proxy {proxy_url}: {e}")
               pass
            finally:
                progress_update[0] += 1  # Increment total attempts

    async def verify_proxies(
        self,
        ctx: commands.Context,
        max_concurrent=100,
        max_timeout=10,
        update_interval=3,
    ):
        """
        Verifies all fetched proxies concurrently using a semaphore to limit concurrency.
        Sends periodic updates on progress.
        """
        self.verified_proxies.clear()  # Clear old list of working proxies
        semaphore = asyncio.Semaphore(
            max_concurrent
        )  # Limit the number of concurrent verifications
        progress_update = [0, 0, 0]  # [total attempted, verified found, cancelled]

        # Get the real IP of the machine before starting verification
        await self.get_real_ip()

        if not self.real_ip:
            await ctx.send("Failed to get real IP. Proxy verification aborted.")
            return

        async def progress_report():
            while progress_update[0] < len(self.proxies):
                await ctx.message.edit(
                    content=f"Verifying proxies: ({progress_update[0]}/{len(self.proxies)}), {progress_update[1]} verified found."
                )
                await asyncio.sleep(update_interval)

        timeout = aiohttp.ClientTimeout(total=max_timeout)
        # Start verification tasks
        verify_tasks = [
            self.verify_proxy(proxy, timeout, semaphore, progress_update)
            for proxy in self.proxies
        ]

        # Run progress report concurrently with verification
        report_task = asyncio.create_task(progress_report())

        try:
            await asyncio.gather(*verify_tasks)
        except asyncio.CancelledError:
            pass
            # await ctx.send("Verification task was canceled.")
        finally:
            # Cancel progress report when verification is done or canceled
            report_task.cancel()

    @commands.command(name="fetch_proxies", aliases=["fp"])
    async def fetch_and_verify_proxies_command(
        self, ctx: commands.Context, max_concurrent=100, max_timeout=3
    ) -> None:
        """
        Command to fetch proxies and verify them concurrently, with progress updates.
        """
        if self.proxy_task and not self.proxy_task.done():
            await ctx.message.edit(
                "There is already an ongoing proxy verification process. Please cancel it first or wait for it to complete."
            )
            return

        await ctx.message.edit("Fetching and verifying proxies...")

        # Clear the current proxy list before fetching new ones
        self.proxies.clear()
        self.seen_origins.clear()

        # Fetch the proxies from all sources
        await self.fetch_proxies()

        if not self.proxies:
            await ctx.message.edit("No proxies found.")
            return

        # Start the verification task and store the reference
        self.proxy_task = asyncio.create_task(
            self.verify_proxies(
                ctx, max_concurrent=max_concurrent, max_timeout=max_timeout
            )
        )

        try:
            # Wait for the task to complete
            await self.proxy_task

            # Final update after verification
            if self.verified_proxies:
                await ctx.message.edit(
                    f"Verification complete. {len(self.verified_proxies)} working proxies found."
                )
            else:
                await ctx.message.edit("No working proxies found.")
        except asyncio.CancelledError:
            await ctx.message.edit(
                f"Proxy scraping was canceled early. {len(self.verified_proxies)} working proxies found."
            )

    @commands.command(name="cancel_proxy_scan", aliases=["cp"])
    async def cancel_proxy_scan(self, ctx: commands.Context) -> None:
        """
        Command to cancel the current proxy verification process.
        """
        if self.proxy_task and not self.proxy_task.done():
            self.proxy_task.cancel()  # Cancel the task
            await ctx.message.delete()
        else:
            await ctx.message.edit("No proxy verification process is running.")

    @commands.command(name="show_proxies")
    async def show_proxies(
        self, ctx: commands.Context, limit=100_000, batch=20
    ) -> None:
        """
        Command to show the verified proxies.
        """
        if not self.verified_proxies:
            await ctx.message.edit(
                f"No working proxies available. Use one of the prefixes in `{self.bot.prefixes}` and for example, do {random.choice(self.bot.prefixes)}fetch_proxies to fetch and verify some."
            )
            return

        # Send proxies in batches of 10 to avoid hitting the Discord character limit
        for i in range(0, min(limit, len(self.verified_proxies)), batch):
            proxies_batch = "\n".join(self.verified_proxies[i : i + batch])
            await ctx.send(f"```\n{proxies_batch}\n```")

    @commands.command(name="proxy_file", aliases=["pf"])
    async def save_proxies_to_file(self, ctx: commands.Context) -> None:
        """
        Command to send the proxies as a file to Discord.
        """
        if not self.verified_proxies:
            await ctx.message.edit(
                f"No working proxies available. Use one of the prefixes in `{self.bot.prefixes}` and for example, do {random.choice(self.bot.prefixes)}fetch_proxies to fetch and verify some."
            )
            return

        # sort the proxies before saving (to easily see duplicates)
        self.verified_proxies.sort()

        memory_file = io.BytesIO()
        memory_file.write("\n".join(self.verified_proxies).encode())
        memory_file.seek(0)

        await ctx.message.delete()
        # Send the file to Discord
        await ctx.send(file=discord.File(memory_file, filename="proxies.txt"))


async def setup(bot: commands.Bot) -> None:
    """
    Adds the ProxyFetcher cog to the bot.
    """
    proxies = Proxies(bot)
    await proxies.r
    await bot.add_cog()
