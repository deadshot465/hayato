import typing

import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name

__info: typing.Final[str] = 'Welcome to the lottery hosted by Hayato!\n\nTo join the lottery, you need to set up an' \
                            ' account first. You can buy your first lottery for free and set up an account. The' \
                            ' command will be `/lottery <numbers>` (numbers must be separated by a comma). You' \
                            ' need to choose exactly 6 distinct numbers between 1 and 49 in order to buy a' \
                            ' lottery ticket.' \
                            ' Or, if you don\'t know what numbers to choose, you can use `/lottery` to let me' \
                            ' choose for you! After that, you will receive 100 starting credits. You can buy more' \
                            ' than one lottery tickets, and each ticket will cost you 10 credits.\n\nModerators' \
                            ' will start the lottery regularly. 6 numbers will be drawn from each lottery. The' \
                            ' reward system is as follows:\n0/1 numbers match: 0 credits\n' \
                            '2 numbers match: 10 credits\n' \
                            '3 numbers match: 50 credits\n' \
                            '4 numbers match: 500 credits\n' \
                            '5 numbers match: 1000 credits\n' \
                            '6 numbers match: 3000 credits\n\nYou can get daily and weekly credits with the command' \
                            ' `/lottery daily` and `/lottery weekly`. Within a 24-hour period, you can receive 10' \
                            ' credits. You can also receive 30 credits for every 7 days. If you don’t have enough' \
                            ' credits, or you want to give some credits to your friends, you can transfer credits' \
                            ' with them. The command is `/lottery transfer <amount> <recipient>`. You must ping' \
                            ' the recipient in order to finish the transaction.\n\nTo see the lotteries you have' \
                            ' bought so far, type `/lottery list`.\n\nGood luck!\n\nExamples of commands:\n' \
                            '`/lottery buy 1,2,3,4,5,6` Correct\n`/lottery buy 1-2-3-4-5-6` Incorrect, numbers must' \
                            ' be separated by comma\n`/lottery buy 2,2,3,5,7,7` Incorrect, numbers cannot be' \
                            ' repeated.'


@lottery.child
@lightbulb.command('info', 'Display information about Hayato\'s lottery game.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def info(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    embed = hikari.Embed(title='Lottery', description=__info, color=HAYATO_COLOR) \
        .set_author(name=author_name, icon=ctx.author.avatar_url or ctx.author.default_avatar_url) \
        .set_thumbnail(LOTTERY_ICON)
    await ctx.respond(embed)
