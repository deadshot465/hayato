import typing

import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name

__info: typing.Final[str] = 'Here is a list of commands available for the lottery.\n\n' \
                            'Create an account/buy a lottery with random numbers: `/lottery`\n' \
                            'Buy a lottery with desired numbers: `/lottery <numbers>` (6 distinct numbers,' \
                            ' separated by commas)\n' \
                            'Get daily/weekly credits: `/lottery daily` / `/lottery weekly`\n' \
                            'Check balance: `/lottery balance`\n' \
                            'Check bought lotteries: `/lottery list`\n' \
                            'Transfer credits to another person: `/lottery transfer <amount> <recipient>`'


@lottery.child
@lightbulb.command('help', 'Display guides and a list of lottery commands.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def help(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    embed = hikari.Embed(title='Lottery commands', description=__info, color=HAYATO_COLOR) \
        .set_author(name=author_name, icon=ctx.author.avatar_url or ctx.author.default_avatar_url) \
        .set_thumbnail(LOTTERY_ICON)
    await ctx.respond(embed)
