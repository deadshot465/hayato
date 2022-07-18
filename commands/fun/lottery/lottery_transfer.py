import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from services.credit_service import credit_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@lottery.child
@lightbulb.option('amount', 'The amount of credits to transfer.', type=int, required=True, min_value=0)
@lightbulb.option('user', 'The user to whom you want to transfer credits.', type=hikari.User, required=True)
@lightbulb.command('transfer', 'Transfer your credits to another member.', auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def transfer(ctx: lightbulb.Context) -> None:
    if ctx.options.amount < 0:
        await ctx.respond(content='You can\'t trade with negative amounts!')
        return

    author_id = ctx.author.id
    author_name = get_author_name(ctx.author, ctx.member)
    credits_1 = await credit_service.get_user_credits(int(author_id), author_name)

    target_user = ctx.get_guild().get_member(ctx.options.user)
    if target_user is None:
        await ctx.respond(content='Sorry, I can\'t seem to find the user you mentioned!')
        return

    target_user_name = get_author_name(ctx.options.user, target_user)
    await credit_service.get_user_credits(int(target_user.id), target_user_name)

    amount: int = ctx.options.amount
    if credits_1 - amount < 0:
        await ctx.respond(content='You cannot transfer more credits than you currently have!')
        return
    elif amount < 0:
        await ctx.respond(content='You can\'t trade with negative amounts!')
        return

    author_credit_item = await credit_service \
        .remove_credits(user_id=int(author_id), user_name=author_name, amount=amount)
    await credit_service.add_credits(user_id=int(target_user.id),
                                     user_name=target_user_name,
                                     amount=amount)

    embed = hikari.Embed(title='Transfer Credits',
                         description='%s has transferred %d credits to %s!' %
                                     (author_name, amount, target_user_name), color=HAYATO_COLOR) \
        .set_author(name=author_name, icon=ctx.author.avatar_url or ctx.author.default_avatar_url) \
        .add_field('Balance', str(author_credit_item.credits), inline=False) \
        .set_thumbnail(LOTTERY_ICON)
    await ctx.respond(embed=embed)
