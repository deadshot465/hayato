import random
import typing

import hikari
from commands.fun.lottery.lottery import Lottery
from lightbulb import slash_commands
from services.lottery_service import lottery_service
from utils.utils import get_author_name


@Lottery.subcommand()
class Buy(slash_commands.SlashSubCommand):
    description: str = 'Buy one and let Hayato decide the numbers for you, or decide yourself!'
    enabled_guilds: list[int] = [705036924330704968]
    numbers: typing.Optional[str] = slash_commands.Option('(Optional) The numbers you want to buy for a lottery.')

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        channel = context.get_channel()
        if channel is not None and channel.type == hikari.ChannelType.DM:
            await context.respond('The lottery game can only be played in guild channels!')
            return
        await context.respond('Alright! Just hold on a second...')
        user_name = get_author_name(context.author, context.member)
        user_id = context.author.id
        if context.option_values.numbers is None:
            result = await lottery_service.buy_lottery(int(user_id), user_name, self.__random_lottery())
        else:
            numbers = self.__validate_numbers(context.option_values.numbers)
            if numbers is None:
                await context.edit_response(
                    content='You either have invalid characters/numbers in the input, or you did\'t provide'
                            ' enough numbers!')
                return
            result = await lottery_service.buy_lottery(int(user_id), user_name, numbers)
        await context.edit_response(content=result)

    @staticmethod
    def __random_lottery() -> set[int]:
        numbers: set[int] = set()
        while len(numbers) < 6:
            numbers.add(random.randint(1, 49))
        return numbers

    @staticmethod
    def __validate_numbers(raw_input: str) -> typing.Optional[set[int]]:
        numbers = [int(x) for x in map(lambda s: s.strip(), raw_input.strip().split(','))
                   if x.isdigit() and 1 <= int(x) <= 49]
        sanitized_numbers = set(numbers)
        if len(sanitized_numbers) != 6:
            return None
        return sanitized_numbers
