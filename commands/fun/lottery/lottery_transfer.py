import hikari
from lightbulb import slash_commands

from commands.fun.lottery.lottery import Lottery
from services.credit_service import credit_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@Lottery.subcommand()
class Transfer(slash_commands.SlashSubCommand):
    description: str = 'Transfer your credits to another member.'
    enabled_guilds: list[int] = [705036924330704968]
    amount: int = slash_commands.Option('The amount of credits to transfer.')
    user: hikari.User = slash_commands.Option('The user to whom you want to transfer credits.')

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        if context.option_values.amount < 0:
            await context.respond('You can\'t trade with negative amounts!')
            return

        author_id = context.author.id
        author_name = get_author_name(context.author, context.member)
        credits_1 = await credit_service.get_user_credits(int(author_id), author_name)

        target_user = context.get_guild().get_member(context.option_values.user)
        if target_user is None:
            await context.respond('Sorry, I can\'t seem to find the user you mentioned!')
            return

        target_user_name = get_author_name(context.option_values.user, target_user)
        await credit_service.get_user_credits(int(target_user.id), target_user_name)

        amount: int = context.option_values.amount
        if credits_1 - amount < 0:
            await context.respond('You cannot transfer more credits than you currently have!')
            return

        await context.respond('Hold on a second...')
        author_credit_item = await credit_service \
            .remove_credits(user_id=int(author_id), user_name=author_name, amount=amount)
        await credit_service.add_credits(user_id=int(target_user.id),
                                         user_name=target_user_name,
                                         amount=amount)

        embed = hikari.Embed(title='Transfer Credits',
                             description='%s has transferred %d credits to %s!' %
                                         (author_name, amount, target_user_name), color=HAYATO_COLOR) \
            .set_author(name=author_name, icon=context.author.avatar_url or context.author.default_avatar_url) \
            .add_field('Balance', str(author_credit_item.Credits), inline=False)\
            .set_thumbnail(LOTTERY_ICON)
        await context.edit_response(embed=embed, content='')
