import random

import lightbulb

from services.credit_service import credit_service
from utils.utils import get_author_name

__choices = ['head', 'tail']


@lightbulb.option('amount', 'The amount of credits you want to bet on.', required=True, type=int)
@lightbulb.option('head_or_tail', 'Guess whether the coin is head or tail.', required=True, choices=['head', 'tail'])
@lightbulb.command(name='coin_flip', description='Play a coinflip game with Hayato.', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def coin_flip(ctx: lightbulb.Context) -> None:
    user_choice: str = ctx.options.head_or_tail.lower()
    amount: int = ctx.options.amount
    user_id = ctx.author.id
    user_name = get_author_name(ctx.author, ctx.member)

    if amount < 0:
        await ctx.respond(content='You cannot input non-positive values of credits!')
        return

    answer = random.choice(__choices)
    if answer == user_choice:
        await credit_service.add_credits(user_id=int(user_id), user_name=user_name, amount=amount)
        await ctx.respond(content='It is **%s**! You gained %d credits!' %
                                  (answer, amount))
    else:
        await credit_service.remove_credits(user_id=int(user_id), user_name=user_name, amount=amount)
        await ctx.respond(content='It is **%s**! You lost %d credits!' %
                                  (answer, amount))
