import datetime
import random

from lightbulb import slash_commands


class Ping(slash_commands.SlashCommand):
    description: str = 'Play a ping-pong message with Hayato and check if Hayato is fine.'
    ping_msgs = ['Pong', 'Pang', 'Peng', 'Pung']

    async def callback(self, context) -> None:
        ping_msg = random.choice(self.ping_msgs)
        start_time = datetime.datetime.now()
        await context.respond('🚅 Pinging...')
        end_time = datetime.datetime.now()
        elapsed = round((end_time - start_time).total_seconds() * 1000, 3)
        await context.edit_response(content=f'🚅 {ping_msg}!\nLatency is: {elapsed}ms. Heartbeat latency is: '
                                            f'{self.bot.heartbeat_latency}ms')
