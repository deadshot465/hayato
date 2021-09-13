import typing

import hikari
from commands.fun.lottery.lottery import Lottery
from lightbulb import slash_commands
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@Lottery.subcommand()
class Help(slash_commands.SlashSubCommand):
    description: str = 'Display guides and a list of lottery commands.'
    enabled_guilds: list[int] = [705036924330704968]
    info: typing.Final[str] = 'Here is a list of commands available for the lottery.\n\n' \
                              'Create an account/buy a lottery with random numbers: `/lottery`\n' \
                              'Buy a lottery with desired numbers: `/lottery <numbers>` (6 distinct numbers,' \
                              ' separated by commas)\n' \
                              'Get daily/weekly credits: `/lottery daily` / `/lottery weekly`\n' \
                              'Check balance: `/lottery balance`\n' \
                              'Check bought lotteries: `/lottery list`\n' \
                              'Transfer credits to another person: `/lottery transfer <amount> <recipient>`'

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        author_name = get_author_name(context.author, context.member)
        embed = hikari.Embed(title='Lottery commands', description=self.info, color=HAYATO_COLOR)\
            .set_author(name=author_name, icon=context.author.avatar_url or context.author.default_avatar_url)\
            .set_thumbnail(LOTTERY_ICON)
        await context.respond(embed)