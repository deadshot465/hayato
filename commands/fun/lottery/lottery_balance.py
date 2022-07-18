import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@lottery.child
@lightbulb.command(name='balance', description='Show your current credit balance.', auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def balance(ctx: lightbulb.Context) -> None:
    await ctx.respond('Hold on a second...')
    author_name = get_author_name(ctx.author, ctx.member)
    user_lottery = await lottery_service.get_user_lottery(int(ctx.author.id))
    if user_lottery is None:
        await ctx.respond(content='You need to create an account by buying a lottery first!')
        return

    user_credit = await credit_service.get_user_credits(int(ctx.author.id), author_name, True)

    embed = hikari.Embed(title='Account Balance',
                         description='Here is your account balance.', color=HAYATO_COLOR) \
        .set_author(name=author_name, icon=ctx.author.avatar_url or ctx.author.default_avatar_url) \
        .set_thumbnail(LOTTERY_ICON) \
        .add_field(name='Credits', value=str(user_credit), inline=True)
    await ctx.respond(embed=embed)
