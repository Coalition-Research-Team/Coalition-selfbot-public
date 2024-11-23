import asyncio
import subprocess
import discord
from discord.ext import commands
import traceback
import textwrap
import io
import contextlib

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.discord_bot import CoalitionBot

class Admin(commands.Cog):
    
    def __init__(self, bot: 'CoalitionBot'):
        self.bot = bot
        self.running_bash_processes: list[asyncio.subprocess.Process] = []  # Track running Bash processes
        self.bash_stdout_log = ""  # Store stdout logs
        self.bash_stderr_log = ""  # Store stderr logs

    @commands.command(name="pyeval", aliases=["pyev", "python", "py"])
    # @commands.is_owner()  # Ensures only the bot owner can run this command
    async def eval_fn(self, ctx: commands.Context, *, code: str) -> None:
        """
        Evaluates Python code and returns the output and/or error.
        
        Args:
            code (str): The Python code to evaluate.
        """
        
        
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

    async def stream_subprocess(self, process: asyncio.subprocess.Process, stdout_callback, stderr_callback):
        """
        Helper to stream stdout and stderr asynchronously and pass data to callbacks.
        """
        async def stream_output(stream: asyncio.StreamReader, callback):
            while True:
                line = await stream.readline()
                if line:
                    callback(line.decode())
                else:
                    break

        stdout_task = asyncio.create_task(stream_output(process.stdout, stdout_callback))
        stderr_task = asyncio.create_task(stream_output(process.stderr, stderr_callback))
        await asyncio.wait([stdout_task, stderr_task])

    async def run_bash_in_thread(self, process: asyncio.subprocess.Process):
        """
        Executes a Bash script asynchronously and streams stdout and stderr in real-time.
        """

        # Callbacks for stdout and stderr to handle real-time streaming
        def append_stdout(line):
            self.bash_stdout_log += line

        def append_stderr(line):
            self.bash_stderr_log += line

        # Stream stdout and stderr
        await self.stream_subprocess(process, append_stdout, append_stderr)

        # Wait for the process to finish
        await process.wait()
        return process

    @commands.command(name="bash", aliases=['b', 'sh'])
    async def bash(self, ctx: commands.Context, *, script: str) -> None:
        """
        Executes a Bash script asynchronously and updates stdout/stderr messages in real time.
        """
        
        def fmt_org(script: str, success=True) -> str:
            script = f'```bash\n{script}\n```'
            return f'**{"SUCCESS" if success else "FAILURE"}**: {script}'
        
        # Strip code block markers (```bash and ```)
        if script.startswith("```bash") and script.endswith("```"):
            script = script[7:-3].strip()
        elif script.startswith("```sh") and script.endswith("```"):
            script = script[5:-3].strip()

        try:
            # Create placeholders for stdout and stderr messages
            await ctx.message.edit(fmt_org(script))
            stdoutMsg = await ctx.send('```bash\nstdout:\nInitializing...\n```')
            stderrMsg = await ctx.send('```bash\nstderr:\nInitializing...\n```')

            self.bash_stdout_log = ""
            self.bash_stderr_log = ""
            
            process = await asyncio.create_subprocess_shell(
                script,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Callback to update stdoutMsg and stderrMsg with real-time output
            async def update_stdout():
                last_tail = ""
                while True:
                    if process.returncode is not None:  # Break when process finishes
                        break
                    
                    await asyncio.sleep(1)  # Update every 1 second
                    stdout_tail = self.bash_stdout_log[-1500:]
                    if stdout_tail == last_tail:
                        continue
                    last_tail = stdout_tail
                    await stdoutMsg.edit(content=f'```bash\nstdout:\n{stdout_tail}\n```')

            async def update_stderr():
                last_tail = ""
                while True:
                    if process.returncode is not None:  # Break when process finishes
                        break
                    
                    await asyncio.sleep(1)  # Update every 1 second
                    stderr_tail = self.bash_stderr_log[-1500:]
                    if stderr_tail == last_tail:
                        continue
                    last_tail = stderr_tail
                    await stderrMsg.edit(content=f'```bash\nstderr:\n{stderr_tail}\n```')

            # Run the bash command in a separate thread and update outputs in real time
            
            # Start the tasks to update stdout and stderr in real time
            await asyncio.gather(self.run_bash_in_thread(process=process), update_stdout(), update_stderr())

            # Once the process finishes, ensure the logs are fully updated
            stdout_tail = self.bash_stdout_log[-1500:]
            stderr_tail = self.bash_stderr_log[-1500:]
            if not stdout_tail:
                stdout_tail = "No output."
            if not stderr_tail:
                stderr_tail = "No output."
            await stdoutMsg.edit(content=f'```bash\nstdout:\n{stdout_tail}\n```')
            await stderrMsg.edit(content=f'```bash\nstderr:\n{stderr_tail}\n```')

        except Exception as e:
            await ctx.message.edit(fmt_org(script, False))
            await stderrMsg.edit(content=f'```bash\nException:\n{str(e)}\n```')

    @commands.command(name="bash_log", aliases=['blog', 'bl'])
    async def bash_log(self, ctx: commands.Context) -> None:
        """
        Retrieves the stored stdout and stderr logs and sends them as files.
        """
        if not self.bash_stdout_log and not self.bash_stderr_log:
            await ctx.send("No logs available.")
            return

        # Create files from stdout and stderr logs
        stdout_file = io.StringIO(self.bash_stdout_log)
        stderr_file = io.StringIO(self.bash_stderr_log)
        
        stdout_file.seek(0)
        stderr_file.seek(0)

        # Send the logs as files
        await ctx.send("Here are the Bash logs:", files=[
            discord.File(stdout_file, "stdout.log"),
            discord.File(stderr_file, "stderr.log")
        ])

    @commands.command(name="halt_bash", aliases=["stop_bash", "bstop"])
    async def halt_bash(self, ctx: commands.Context) -> None:
        """
        Halts all currently running Bash scripts.
        """
        if not self.running_bash_processes:
            await ctx.message.edit("No Bash scripts are currently running.")
            return

        for process in self.running_bash_processes:
            if process.returncode is None:  # Check if the process is still running
                process.terminate()  # Terminate the process

        self.running_bash_processes.clear()  # Clear the list of processes
        await ctx.message.edit("All running Bash scripts have been halted.")



async def setup(bot: commands.Bot) -> None:
    """
    Adds the Eval cog to the bot.
    """
    await bot.add_cog(Admin(bot))
