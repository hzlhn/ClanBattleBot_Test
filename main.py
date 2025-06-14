import logging.config
import traceback
from logging import getLogger

import discord
from discord.ext import commands
from setup import TOKEN
from discord import app_commands

logging.config.fileConfig('logging.conf')
logger = getLogger(__name__)

INITIAL_EXTENSIONS = [
    'cogs.clan_battle',
    'cogs.error_handler'
]

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents, help_command=None)

    async def setup_hook(self):
        for cog in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(cog)
            except Exception:
                traceback.print_exc()
        await self.tree.sync()

    async def on_ready(self):
        logger.info("Login was successful.")
        logger.info(f"bot name: {self.user.name}")
        logger.info(f"bot id: {self.user.id}")

async def main():
    intents = discord.Intents(messages=True, guilds=True, members=True, reactions=True)
    bot = MyBot('.', intents)
    await bot.start(TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())