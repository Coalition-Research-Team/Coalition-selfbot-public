# -*- coding: utf-8 -*-
from asyncio.subprocess import Process
import subprocess
from discord.ext import commands
import traceback
import textwrap
import io
import contextlib
import asyncio

from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot

class Admin(commands.Cog):
    
    def __init__(self, bot: 'CoalitionBot'):
        self.bot = bot
        self.running_processes = [] 

    @commands.command(name="pyeval", aliases=["pyev", "python", "py"])
    async def eval_fn(self, ctx: commands.Context, *, code: str) -> None:
        
        def fmt_org(code: str, success=True) -> str:
            code = f'```py\n{code}\n```'
            return f'**{"SUCCESS" if success else "FAILURE"}**: {code}'
                
        
        
        """
        Evaluates Python code.
        """
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message
        }

        # Add the bot and context to the environment
        env.update(globals())

        stripped = False
        # Strip code block markers (``` and ```py)
        if code.startswith("```") and code.endswith("```"):
            stripped = True
            code = code[3:-3]  # Remove the outer ```
            if code.startswith("py"):
                if code.startswith("python"):
                    code = code[6:].strip()
                else:
                    code = code[2:].strip()  # Remove the "py" if it's a Python code block

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f'async def func():\n{textwrap.indent(code, "    ")}', env
                )

                # Execute the function and await the result
                result = await env['func']()
        except Exception as e:
            # Capture the traceback and send it as a message
            await ctx.message.edit(fmt_org(code, False))
            return await ctx.send(f'```py\n{traceback.format_exc()[-1980:]}\n```')

        # Get the output from stdout and send the result
        output = stdout.getvalue()
        if result is None:
            if output:
                await ctx.message.edit(fmt_org(code))
                await ctx.send(f'```py\n{output[:1990]}\n```')
            else:
                await ctx.message.edit(fmt_org(code))
                await ctx.send("```py\nNo output produced.\n```")
        else:
            await ctx.message.edit(fmt_org(code))
            await ctx.send(f'```py\n{output}{result[:1990]}\n```')

    async def run_bash(self, script: str) -> Tuple[str, str, Process]:
        """
        Executes the Bash script asynchronously without blocking the main thread.
        """
        process = await asyncio.create_subprocess_shell(
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        self.running_processes.append(process)

        return stdout.decode(), stderr.decode(), process

    @commands.command(name="bash", aliases=['b', 'sh'])
    async def bash(self, ctx: commands.Context, *, script: str) -> None:
        """
        Executes a Bash script asynchronously in a separate thread and returns the output or error.
        The script should be enclosed in a bash code block (```bash <code> ```).
        """
        
        def fmt_org(script: str, success=True) -> str:
            script = f'```bash\n{script}\n```'
            return f'**{"SUCCESS" if success else "FAILURE"}**: {script}'
        
        # Strip code block markers (```bash and ```)
        if script.startswith("```bash") and script.endswith("```"):
            script = script[7:-3].strip()  # Remove ```bash from the start and ``` from the end
        elif script.startswith("```sh") and script.endswith("```"):
            script = script[5:-3].strip()

        try:
            # Execute the script in a separate thread
            stdout, stderr, process = await self.run_bash(script)

            # If there's output, send it back
            if stdout:
                await ctx.message.edit(fmt_org(script))
                await ctx.send(f'```bash\n{stdout[-1980:]}\n```')

            # If there's an error, send the error message
            if stderr:
                await ctx.message.edit(fmt_org(script, False))
                await ctx.send(f'```bash\nError:\n{stderr[-1980:]}\n```')

            # If there's no output or error, let the user know
            if not stdout and not stderr:
                await ctx.message.edit(fmt_org(script))
                await ctx.send(f'```bash\nCommand executed successfully but produced no output.\n```')

        except Exception as e:
            # Catch any exceptions and return the error
            await ctx.message.edit(fmt_org(script, False))
            await ctx.send(f'```bash\nException:\n{str(e)}\n```')
            
            
    @commands.command(name="halt_bash", aliases=["stop_bash", "bstop"])
    async def halt_bash(self, ctx: commands.Context) -> None:
        """
        Halts all currently running Bash scripts.
        """
        if not self.running_processes:
            await ctx.message.edit("No Bash scripts are currently running.")
            return

        # Terminate all running processes
        for process in self.running_processes:
            if process.returncode is None:  # Check if the process is still running
                process.terminate()
                await process.wait()

        self.running_processes.clear()  # Clear the list of processes
        await ctx.message.edit("All running Bash scripts have been halted.")


async def setup(bot: commands.Bot) -> None:
    """
    Adds the Eval cog to the bot.
    """
    await bot.add_cog(Admin(bot))
