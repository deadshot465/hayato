import asyncio
import logging
import random
import typing

import hikari
import lightbulb

from commands.fun.eight_ball import EightBall
from commands.fun.lottery import lottery, lottery_balance, lottery_buy, lottery_daily, lottery_help, lottery_info,\
    lottery_list, lottery_weekly
from commands.info.about import About
from commands.info.guild import Guild
from commands.info.ping import Ping
from commands.rails import jrwest, mtr, rails, shinkansen, toei, tokyo_metro

from services.configuration_service import configuration_service


def initialize_railway_lines():
    _ = jrwest.JrWest(bot)
    _ = mtr.Mtr(bot)
    _ = tokyo_metro.TokyoMetro(bot)
    _ = toei.Toei(bot)
    _ = shinkansen.Shinkansen(bot)
    _ = shinkansen.Line(bot)
    _ = shinkansen.Train(bot)


def initialize_lottery_commands():
    _ = lottery_buy.Buy(bot)
    _ = lottery_info.Info(bot)
    _ = lottery_list.List(bot)
    _ = lottery_help.Help(bot)
    _ = lottery_balance.Balance(bot)
    _ = lottery_daily.Daily(bot)
    _ = lottery_weekly.Weekly(bot)


token = configuration_service.token
prefix = configuration_service.prefix
log_level = configuration_service.log_level

bot = lightbulb.Bot(prefix=prefix, token=token, logs=log_level, intents=hikari.Intents.ALL)
cmds: list[typing.Type[lightbulb.slash_commands.BaseSlashCommand]] =\
    [About, EightBall, Guild, lottery.Lottery, Ping, rails.Rails]
initialize_railway_lines()
initialize_lottery_commands()
for cmd in cmds:
    bot.add_slash_command(cmd)


async def set_initial_presence():
    activity = hikari.Activity(name=random.choice(configuration_service.trains), type=hikari.ActivityType.PLAYING)
    await bot.update_presence(activity=activity)
    asyncio.create_task(update_presence())


async def update_presence():
    try:
        await asyncio.sleep(3600)
        new_activity = hikari.Activity(name=random.choice(configuration_service.trains),
                                       type=hikari.ActivityType.PLAYING)
        await bot.update_presence(activity=new_activity)
        asyncio.create_task(update_presence())
    except Exception as e:
        logging.error(e)


@bot.listen()
async def ready(_: hikari.ShardReadyEvent):
    await set_initial_presence()
    configuration_service.bot = bot

bot.run(asyncio_debug=True)