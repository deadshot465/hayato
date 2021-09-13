import random
import typing

from lightbulb import slash_commands
from services.credit_service import credit_service
from utils.utils import get_author_name


class CoinFlip(slash_commands.SlashCommand):
    description: str = 'Play a coinflip game with Hayato.'
    enabled_guilds: list[int] = [705036924330704968]
    head_or_tail: str = slash_commands.Option('Guess whether the coin is head (h, hd) or tail (t, tl).')
    amount: int = slash_commands.Option('The amount of credits you want to bet on.')

    _choices: typing.Final[list[str]] = ['h', 't']
    _heads: typing.Final[list[str]] = ['h', 'hd', 'head']
    _tails: typing.Final[list[str]] = ['t', 'tl', 'tail']
    _mapping: typing.Final[dict[str, str]] = {
        'h': 'head',
        't': 'tail'
    }

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        user_choice: str = context.option_values.head_or_tail.lower()
        amount: int = context.option_values.amount
        user_id = context.author.id
        user_name = get_author_name(context.author, context.member)

        if (user_choice not in self._heads) and (user_choice not in self._tails):
            await context.respond('You need to guess if it is head or tail. The correct input is: '
                                  '`/coinflip <h/t> <amount>`')
            return

        if amount < 0:
            await context.respond('You cannot input non-positive values of credits!')
            return

        await context.respond('Alright! Hold on a second...')

        answer = random.choice(self._choices)
        if answer == user_choice[0]:
            await credit_service.add_credits(user_id=int(user_id), user_name=user_name, amount=amount)
            await context.edit_response(content='It is **%s**! You gained %d credits!' %
                                                (self._mapping[answer], amount))
        else:
            await credit_service.remove_credits(user_id=int(user_id), user_name=user_name, amount=amount)
            await context.edit_response(content='It is **%s**! You lost %d credits!' %
                                                (self._mapping[answer], amount))
