import random
import typing

from lightbulb import slash_commands
from utils.utils import get_author_name


class CoinFlip(slash_commands.SlashCommand):
    description: str = 'Play a coinflip game with Hayato.'
    enabled_guilds: list[int] = [705036924330704968]
    question: str = slash_commands.Option('The question you want to ask Hayato.')

    EIGHTBALL_RESPONSE: typing.Final[list[str]] = \
        ['Of course', 'It is certain', 'I think so', 'Maybe', 'If you like Shinkansen, then yes',
         'I think this is as reliable as Shinkansen trains', 'This is as good as E5 Series',
         'Uhh...I am not sure', 'I don\'t want to tell you now, because I am watching Shinkalion now',
         'This question is like asking me if Shinkansen is rapid or not',
         'I am tired now, ask me later', 'Sorry, I don\'t know',
         'Think about it again and ask me later',
         'Definitely no', 'Of course no, don\'t ask me the same question again', 'I guess no',
         'Maybe not']

    async def callback(self, context) -> None:
        choice = random.choice(self.EIGHTBALL_RESPONSE)
        await context.respond('🎱 | {}, **{}**!'.format(choice, get_author_name(context.author, context.member)))
