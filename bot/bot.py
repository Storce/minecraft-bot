import os
import discord
import logging
from discord.ext import tasks
from google import genai
from mcrcon import MCRcon

# 1. Setup Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
RCON_PASSWORD = os.getenv('RCON_PASSWORD')
LOG_PATH = "/data/logs/latest.log"

try:
    CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
except (TypeError, ValueError):
    logger.error("CHANNEL_ID is not set or invalid.")
    exit(1)

genai_client = genai.Client(api_key=GEMINI_API_KEY)

class LogBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_pos = 0

    async def setup_hook(self):
        logger.info("Bot initializing and starting log-read loop...")
        self.read_logs.start()

    def send_rcon_cmd(self, command):
        try:
            with MCRcon("mc-server", RCON_PASSWORD, port=25595) as mcr:
                return mcr.command(command)
        except Exception as e:
            logger.error(f"RCON Connection Failed: {e}")
            return None

    async def handle_gemini_query(self, query):
        logger.info(f"Trigger: Gemini request received: '{query}'")
        self.send_rcon_cmd("I've sent a message to Steve!")
        
        prompt = (f"Context: You are Steve from Minecraft. Respond concisely (max 3 sentences) "
                  f"referencing blocks or Minecraft mechanics. Question: {query}")
        
        try:
            response = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            clean_response = response.text.strip().replace('\n', ' ')
            logger.info("Gemini API successful.")
            self.send_rcon_cmd(f"say {clean_response}")
        except Exception as e:
            logger.error(f"Gemini API failed: {e}")
            self.send_rcon_cmd(f"A creeper blew up the messager: {str(e)[:50]}")

    @tasks.loop(seconds=2)
    async def read_logs(self):
        if not os.path.exists(LOG_PATH):
            return

        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            return

        with open(LOG_PATH, 'r', errors='ignore') as f:
            if self.last_pos == 0:
                f.seek(0, os.SEEK_END)
                self.last_pos = f.tell()
                return

            f.seek(self.last_pos)
            lines = f.readlines()
            self.last_pos = f.tell()

            for line in lines:
                msg = None
                
                if "--yo" in line:
                    query = line.split("--yo")[1].strip()
                    await self.handle_gemini_query(query)

                if "joined the game" in line:
                    user = line.split("]: ")[1].split(" joined")[0]
                    logger.info(f"Trigger: Player Join - {user}")
                    msg = f"🟢 **{user}** joined"
                elif "left the game" in line:
                    user = line.split("]: ")[1].split(" left")[0]
                    logger.info(f"Trigger: Player Leave - {user}")
                    msg = f"🔴 **{user}** left"
                elif "Can't keep up!" in line:
                    logger.warning("Trigger: Server Lag Detected")
                    msg = "⚠️ **Server Lag Detected**"
                elif "[Server thread/INFO]: <" in line:
                    user = line.split("<")[1].split(">")[0]
                    content = line.split("> ")[1].strip()
                    logger.info(f"Trigger: Chat Message from {user}")
                    msg = f"💬 **{user}**: {content}"

                if msg:
                    await channel.send(msg)

    @read_logs.before_loop
    async def before_read_logs(self):
        await self.wait_until_ready()
        logger.info("Discord client ready.")

intents = discord.Intents.default()
client = LogBot(intents=intents)
client.run(TOKEN)
