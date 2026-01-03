This simple docker compose runs a minecraft server and a Discord bot that tracks the server's logs and execute commands using RCON. 
## Setup
1. Add DISCORD_TOKEN and CHANNEL_ID to .env for the discord bot
2. If you want AI, add GEMINI_APY_KEY to .env
3. Add a **strong** password RCON_PASSWORD to .env
2. To run a modpack, download its server files, unzip it, and copy its content to `./data`. To run vanilla server, leave it as it is.
3. Check compatible forge, java, and minecraft versions and edit the docker compose file
4. Run `docker compose up --build`

## Feature
1. [Passive] Logs player logons and logoffs to selected Discord channel.
2. [Passive] logs server overload warning to selected Discord channel.
3. Send messages with prefix `--yo` in Minecraft to ask AI questions (e.g. `--yo how to make an iron farm`)


