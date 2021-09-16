import asyncio
import datetime
import logging
import os
import random
import typing

import hikari
import lightbulb

from commands.admin import admin
from commands.fun.coinflip import CoinFlip
from commands.fun.eight_ball import EightBall
from commands.fun.lottery import lottery, lottery_balance, lottery_buy, lottery_daily, lottery_help, lottery_info,\
    lottery_list, lottery_start, lottery_transfer, lottery_weekly
from commands.info.about import About
from commands.info.guild import Guild
from commands.info.ping import Ping
from commands.rails import jrwest, mtr, rails, shinkansen, toei, tokyo_metro
from commands.utility.pick import Pick

from services.configuration_service import configuration_service
from services.lottery_service import lottery_service


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
    _ = lottery_start.Start(bot)
    _ = lottery_transfer.Transfer(bot)


if os.name != 'nt':
    import uvloop
    uvloop.install()


token = configuration_service.token
prefix = configuration_service.prefix
log_level = configuration_service.log_level

bot = lightbulb.Bot(prefix=prefix, token=token, logs=log_level,
                    intents=hikari.Intents.ALL, delete_unbound_slash_commands=False,
                    recreate_changed_slash_commands=False)
cmds: list[typing.Type[lightbulb.slash_commands.BaseSlashCommand]] =\
    [About, admin.Admin, CoinFlip, EightBall, Guild, lottery.Lottery, Pick, Ping, rails.Rails]
initialize_railway_lines()
initialize_lottery_commands()
for cmd in cmds:
    bot.add_slash_command(cmd)


@bot.listen()
async def message_create(e: hikari.GuildMessageCreateEvent):
    if e.author.is_bot:
        return

    ignored_channels = configuration_service.ignored_channels
    if int(e.channel_id) in ignored_channels:
        return

    bot_user = bot.get_me()
    msg = e.message
    lowercase_content = msg.content.lower()
    chance = random.randint(1, 100)
    if bot_user.mention in lowercase_content or 'hayato' in lowercase_content:
        if chance > configuration_service.mention_reply_chance:
            await e.get_channel().send(random.choice(configuration_service.responses))
    else:
        if chance > configuration_service.random_reply_chance:
            await e.get_channel().send(random.choice(configuration_service.responses))


@bot.listen()
async def ready(_: hikari.ShardReadyEvent):
    await set_initial_presence()
    configuration_service.bot = bot
    asyncio.create_task(schedule_lottery())
    from commands.utility.eval import evaluate


async def schedule_lottery():
    next_lottery_time = lottery_service.lottery_scheduled
    seconds = (next_lottery_time - datetime.datetime.now()).total_seconds()
    while seconds < 0.0:
        lottery_service.set_next_lottery_time()
        next_lottery_time = lottery_service.lottery_scheduled
        seconds = (next_lottery_time - datetime.datetime.now()).total_seconds()
    try:
        await asyncio.sleep(seconds)
        channel = bot.cache.get_guild_channel(lottery_service.lottery_channel_id)
        await lottery_service.auto_lottery(channel)
        lottery_service.set_next_lottery_time()
        asyncio.create_task(schedule_lottery())
    except Exception as e:
        logging.error(e)


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


if __name__ == '__main__':
    logging.info('Hayato is loaded.')

bot.run()
