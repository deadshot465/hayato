import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from services.lottery_service import lottery_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@lottery.child
@lightbulb.command('list', 'Show your currently owned lotteries.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def list_lotteries(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    participant = lottery_service.get_participant(int(ctx.author.id))
    if participant is None:
        await ctx.respond('You are not in the lottery game yet!\nBuy a lottery to join in the game.')
        return

    lottery_count = len(participant.lotteries)
    if lottery_count == 0:
        await ctx.respond('You currently don\'t have any lotteries!')
        return

    lottery_list = list(map(lambda l: '[%s]' % (', '.join(list(map(lambda i: str(i), l)))), participant.lotteries))
    lottery_list_text = '\n'.join(lottery_list)[:1000]

    embed = hikari.Embed(title='Purchased Lotteries',
                         description='You currently have %d lotteries. The following are your currently purchased'
                                     ' lotteries (trimmed).' % lottery_count, color=HAYATO_COLOR) \
        .set_author(name=author_name, icon=ctx.author.avatar_url or ctx.author.default_avatar_url) \
        .set_thumbnail(LOTTERY_ICON) \
        .add_field(name='Lotteries', value=lottery_list_text, inline=False)
    await ctx.respond(embed)
