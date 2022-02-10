import datetime
import random

import lightbulb

__ping_msgs = ['Pong', 'Pang', 'Peng', 'Pung']


@lightbulb.command('ping', 'Play a ping-pong message with Hayato and check if Hayato is fine.')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    ping_msg = random.choice(__ping_msgs)
    start_time = datetime.datetime.now()
    await ctx.respond('🚅 Pinging...')
    end_time = datetime.datetime.now()
    elapsed = round((end_time - start_time).total_seconds() * 1000, 3)
    await ctx.edit_last_response(content=f'🚅 {ping_msg}!\nLatency is: {elapsed}ms. Heartbeat latency is: '
                                         f'{ctx.bot.heartbeat_latency}ms')
