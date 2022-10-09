import asyncio
import datetime
import logging
import os
import random

import hikari
import lightbulb

import services.google_api_service
from commands.admin.admin import admin, allow, ignore, save_to_drive
from commands.fun.coinflip import coin_flip
from commands.fun.eight_ball import eight_ball
from commands.fun.lottery import lottery, lottery_balance, lottery_buy, lottery_daily, lottery_exchange, lottery_help, \
    lottery_info, \
    lottery_list, lottery_start, lottery_transfer, lottery_weekly
from commands.info.about import about
from commands.info.guild import guild_info
from commands.info.ping import ping
from commands.rails import jrwest, mtr, rails, shinkansen, toei, tokyo_metro
from commands.utility.pick import pick
from services.configuration_service import configuration_service
from services.lottery_service import lottery_service

if os.name != 'nt':
    import uvloop

    uvloop.install()

token = configuration_service.token
prefix = configuration_service.prefix
log_level = configuration_service.log_level

bot = lightbulb.BotApp(prefix=prefix, token=token, logs=log_level,
                       intents=hikari.Intents.ALL)

cmds = \
    [about, admin, allow, ignore, coin_flip, eight_ball, guild_info, save_to_drive,
     lottery.lottery,
     lottery_balance.balance,
     lottery_buy.buy,
     lottery_daily.daily,
     lottery_exchange.exchange,
     lottery_help.help,
     lottery_info.info,
     lottery_list.list_lotteries,
     lottery_start.start,
     lottery_transfer.transfer,
     lottery_weekly.weekly,
     pick, ping,
     rails.rails, jrwest.jr_west, mtr.mtr,
     shinkansen.shinkansen,
     shinkansen.line, shinkansen.train,
     toei.toei, tokyo_metro.tokyo_metro]

for cmd in cmds:
    bot.command(cmd)


@bot.listen()
async def message_create(e: hikari.GuildMessageCreateEvent):
    if e.author.is_bot:
        return

    ignored_channels = configuration_service.ignored_channels
    if int(e.channel_id) in ignored_channels:
        return

    bot_user = bot.get_me()
    msg = e.message
    if msg.content is None:
        return

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
    services.google_api_service.initialize()
    logging.info('Hayato is loaded.')

bot.run()
