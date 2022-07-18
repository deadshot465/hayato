import asyncio
import random
import typing

import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


def __random_lottery():
    while True:
        numbers: set[int] = set()
        while len(numbers) < 6:
            numbers.add(random.randint(1, 49))
        yield numbers


async def __bulk_purchase(bot: lightbulb.BotApp, *,
                          amount: int, user_id: int, user_name: str, user_icon_url: str,
                          user_credits: int,
                          channel: hikari.TextableGuildChannel) -> str:
    if user_credits - (10 * amount) < 0:
        maximum_amount = user_credits // 10
        return f'You don\'t have enough credits. You can only purchase {maximum_amount} lotteries at maximum!'

    balance_after = user_credits - (10 * amount)
    description = '%s, you are going to purchase %d lotteries at once. After this action, you will have %d' \
                  ' credits in your account. Do you want to continue?' % (user_name, amount, balance_after)
    embed = hikari.Embed(title='Bulk Purchase', description=description, color=HAYATO_COLOR) \
        .set_author(name=user_name, icon=user_icon_url) \
        .set_thumbnail(LOTTERY_ICON) \
        .set_footer(text='React with ✅ to confirm, react with ❌ to cancel.')
    message = await channel.send(embed=embed)
    await message.add_reaction('✅')
    await message.add_reaction('❌')

    def check(e: hikari.ReactionAddEvent) -> bool:
        return e.user_id == user_id and e.message_id == message.id and \
               (e.emoji_name == '✅' or e.emoji_name == '❌')

    async def cancel() -> str:
        await message.delete()
        return '❌ The action is cancelled.'

    try:
        reaction = await bot.wait_for(hikari.ReactionAddEvent, 30.0, check)
    except asyncio.TimeoutError:
        return await cancel()
    else:
        if reaction.emoji_name == '❌':
            return await cancel()
        else:
            await message.delete()
            numbers = [sorted(next(__random_lottery())) for _ in range(0, amount)]
            return await lottery_service.bulk_purchase(user_id, user_name, numbers)


def __validate_numbers(raw_input: str) -> typing.Optional[set[int]]:
    numbers = [int(x) for x in map(lambda s: s.strip(), raw_input.strip().split(','))
               if x.isdigit() and 1 <= int(x) <= 49]
    sanitized_numbers = set(numbers)
    if len(sanitized_numbers) != 6:
        return None
    return sanitized_numbers


@lottery.child
@lightbulb.option('numbers', 'The numbers you want to buy for a lottery, or '
                             'the amount of lotteries to bulk purchase.'
                             ' Or `all`.', required=False)
@lightbulb.command('buy', 'Buy one and let Hayato decide the numbers for you, or decide yourself!', auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def buy(ctx: lightbulb.Context) -> None:
    channel = ctx.get_channel()
    if (channel is not None and channel.type == hikari.ChannelType.DM) or channel is None:
        await ctx.respond(content='The lottery game can only be played in guild channels!')
        return

    user_name = get_author_name(ctx.author, ctx.member)
    user_id = ctx.author.id
    user_icon_url = ctx.author.avatar_url or ctx.author.default_avatar_url
    user_credits = await credit_service.get_user_credits(int(user_id), user_name, True)

    await ctx.respond(response_type=hikari.interactions.ResponseType.DEFERRED_MESSAGE_CREATE)

    numbers: typing.Optional[str] = ctx.options.numbers
    if numbers is None:
        result = await lottery_service.buy_lottery(int(user_id), user_name, next(__random_lottery()))
        await ctx.respond(content=result)
    elif numbers.isdigit():
        if int(numbers) < 0:
            await ctx.respond(content='You can\'t buy negative amount of lotteries!')
            return

        result = await __bulk_purchase(ctx.bot, amount=int(numbers), user_id=user_id,
                                       user_name=user_name, user_icon_url=str(user_icon_url),
                                       user_credits=user_credits, channel=channel)
        await ctx.respond(content=result)
    elif numbers == 'all':
        result = await __bulk_purchase(ctx.bot, amount=user_credits // 10, user_id=user_id,
                                       user_name=user_name, user_icon_url=str(user_icon_url),
                                       user_credits=user_credits, channel=channel)
        await ctx.respond(content=result)
    else:
        validated_numbers = __validate_numbers(numbers)
        if validated_numbers is None:
            await ctx.respond(content='You either have invalid characters/numbers in the input, or you did\'t provide'
                                      ' enough numbers!')
            return
        result = await lottery_service.buy_lottery(int(user_id), user_name, validated_numbers)
        await ctx.respond(content=result)
