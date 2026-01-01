This simple docker compose runs a minecraft server and a Discord bot that tracks its logs and send some information to you desired Discord channel.

## Setup
1. Add .env for DISCORD_TOKEN and CHANNEL_ID for the discord bot
2. To run a modpack, download its server files, unzip it, and copy its content to `./data`. To run vanilla server, leave it as it is.
3. Check compatible forge, java, and minecraft versions and edit the docker compose file
4. Run `docker compose`

