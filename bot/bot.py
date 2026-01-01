import os
import discord
from discord.ext import tasks

TOKEN = os.getenv('DISCORD_TOKEN')
try:
    CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
except (TypeError, ValueError):
    print("Error: CHANNEL_ID is not set or invalid.")
    exit(1)

LOG_PATH = "/data/logs/latest.log"

class LogBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_pos = 0

    async def setup_hook(self):
        self.read_logs.start()

    @tasks.loop(seconds=2)
    async def read_logs(self):
        if not os.path.exists(LOG_PATH):
            return

        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            return

        with open(LOG_PATH, 'r', errors='ignore') as f:
            # On first run, skip to the end so we don't spam old logs
            if self.last_pos == 0:
                f.seek(0, os.SEEK_END)
                self.last_pos = f.tell()
                return

            f.seek(self.last_pos)
            lines = f.readlines()
            self.last_pos = f.tell()

            for line in lines:
                msg = None
                if "joined the game" in line:
                    user = line.split("]: ")[1].split(" joined")[0]
                    msg = f"🟢 **{user}** joined"
                elif "left the game" in line:
                    user = line.split("]: ")[1].split(" left")[0]
                    msg = f"🔴 **{user}** left"
                elif "Can't keep up!" in line:
                    msg = "⚠️ **Server Lag Detected**"
                elif "[Server thread/INFO]: <" in line:
                    user = line.split("<")[1].split(">")[0]
                    content = line.split("> ")[1].strip()
                    msg = f"💬 **{user}**: {content}"

                if msg:
                    await channel.send(msg)

    @read_logs.before_loop
    async def before_read_logs(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
client = LogBot(intents=intents)
client.run(TOKEN)
