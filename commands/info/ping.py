import datetime
import random

from lightbulb import slash_commands


class Ping(slash_commands.SlashCommand):
    description: str = 'Play a ping-pong message with Hayato and check if Hayato is fine.'
    ping_msgs = ['Pong', 'Pang', 'Peng', 'Pung']
    enabled_guilds: list[int] = [705036924330704968]

    async def callback(self, context) -> None:
        ping_msg = self.ping_msgs[random.randrange(0, len(self.ping_msgs))]
        start_time = datetime.datetime.now()
        await context.respond('🚅 Pinging...')
        end_time = datetime.datetime.now()
        elapsed = round((end_time - start_time).total_seconds() * 1000, 3)
        await context.edit_response(content=f'🚅 {ping_msg}!\nLatency is: {elapsed}ms.')
