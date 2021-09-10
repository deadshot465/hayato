import asyncio
import logging
import random
import typing

import hikari
import lightbulb

from commands.info.about import About
from commands.info.guild import Guild
from commands.info.ping import Ping
from services.configuration_service import configuration_service


token = configuration_service.token
prefix = configuration_service.prefix
log_level = configuration_service.log_level

bot = lightbulb.Bot(prefix=prefix, token=token, logs=log_level, intents=hikari.Intents.ALL)
cmds: list[typing.Type[lightbulb.slash_commands.BaseSlashCommand]] = [About, Guild, Ping]
for cmd in cmds:
    bot.add_slash_command(cmd)


async def set_initial_presence():
    index = random.randrange(0, len(configuration_service.trains))
    activity = hikari.Activity(name=configuration_service.trains[index], type=hikari.ActivityType.PLAYING)
    await bot.update_presence(activity=activity)
    asyncio.create_task(update_presence())


async def update_presence():
    try:
        await asyncio.sleep(3600)
        new_index = random.randrange(0, len(configuration_service.trains))
        new_activity = hikari.Activity(name=configuration_service.trains[new_index], type=hikari.ActivityType.PLAYING)
        await bot.update_presence(activity=new_activity)
        asyncio.create_task(update_presence())
    except Exception as e:
        logging.error(e)


@bot.listen()
async def ready(_: hikari.ShardReadyEvent):
    await set_initial_presence()
    bot_user = bot.get_me()
    configuration_service.bot = bot

bot.run(asyncio_debug=True)
