import asyncio
import random
import typing

import hikari
from commands.fun.lottery.lottery import Lottery
from lightbulb import slash_commands
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@Lottery.subcommand()
class Buy(slash_commands.SlashSubCommand):
    description: str = 'Buy one and let Hayato decide the numbers for you, or decide yourself!'
    enabled_guilds: list[int] = [705036924330704968]
    numbers: typing.Optional[str] = slash_commands.Option('The numbers you want to buy for a lottery, or '
                                                          'the amount of lotteries to bulk purchase.'
                                                          ' Or `all`.')

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        channel = context.get_channel()
        if (channel is not None and channel.type == hikari.ChannelType.DM) or channel is None:
            await context.respond('The lottery game can only be played in guild channels!')
            return

        await context.respond('Alright! Just hold on a second...')
        user_name = get_author_name(context.author, context.member)
        user_id = context.author.id
        user_icon_url = context.author.avatar_url or context.author.default_avatar_url
        user_credits = await credit_service.get_user_credits(int(user_id), user_name, True)

        numbers: typing.Optional[str] = context.option_values.numbers
        if numbers is None:
            result = await lottery_service.buy_lottery(int(user_id), user_name, next(self.__random_lottery()))
        elif numbers.isdigit():
            if int(numbers) < 0:
                await context.edit_response(content='You can\'t buy negative amount of lotteries!')
                return

            result = await self.__bulk_purchase(amount=int(numbers), user_id=user_id,
                                                user_name=user_name, user_icon_url=str(user_icon_url),
                                                user_credits=user_credits, channel=channel)
        elif numbers == 'all':
            result = await self.__bulk_purchase(amount=user_credits // 10, user_id=user_id,
                                                user_name=user_name, user_icon_url=str(user_icon_url),
                                                user_credits=user_credits, channel=channel)
        else:
            validated_numbers = self.__validate_numbers(numbers)
            if validated_numbers is None:
                await context.edit_response(
                    content='You either have invalid characters/numbers in the input, or you did\'t provide'
                            ' enough numbers!')
                return
            result = await lottery_service.buy_lottery(int(user_id), user_name, validated_numbers)
        await context.edit_response(content=result)

    async def __bulk_purchase(self, *,
                              amount: int, user_id: int, user_name: str, user_icon_url: str,
                              user_credits: int,
                              channel: hikari.TextableGuildChannel) -> str:
        if user_credits - (10 * amount) < 0:
            maximum_amount = user_credits // 10
            return f'You don\'t have enough credits. You can only purchase {maximum_amount} lotteries at maximum!'

        balance_after = user_credits - (10 * amount)
        description = '%s, you are going to purchase %d lotteries at once. After this action, you will have %d' \
                      ' credits in your account. Do you want to continue?' % (user_name, amount, balance_after)
        embed = hikari.Embed(title='Bulk Purchase', description=description, color=HAYATO_COLOR)\
            .set_author(name=user_name, icon=user_icon_url)\
            .set_thumbnail(LOTTERY_ICON)\
            .set_footer(text='React with ✅ to confirm, react with ❌ to cancel.')
        message = await channel.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')

        def check(e: hikari.ReactionAddEvent) -> bool:
            return e.user_id == user_id and e.message_id == message.id and\
                   (e.emoji_name == '✅' or e.emoji_name == '❌')

        async def cancel() -> str:
            await message.delete()
            return '❌ The action is cancelled.'

        try:
            reaction = await self.bot.wait_for(hikari.ReactionAddEvent, 30.0, check)
        except asyncio.TimeoutError:
            return await cancel()
        else:
            if reaction.emoji_name == '❌':
                return await cancel()
            else:
                await message.delete()
                numbers = [sorted(next(self.__random_lottery())) for _ in range(0, amount)]
                return await lottery_service.bulk_purchase(user_id, user_name, numbers)

    @staticmethod
    def __random_lottery():
        while True:
            numbers: set[int] = set()
            while len(numbers) < 6:
                numbers.add(random.randint(1, 49))
            yield numbers

    @staticmethod
    def __validate_numbers(raw_input: str) -> typing.Optional[set[int]]:
        numbers = [int(x) for x in map(lambda s: s.strip(), raw_input.strip().split(','))
                   if x.isdigit() and 1 <= int(x) <= 49]
        sanitized_numbers = set(numbers)
        if len(sanitized_numbers) != 6:
            return None
        return sanitized_numbers
