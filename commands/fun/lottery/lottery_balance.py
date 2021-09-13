import hikari
from commands.fun.lottery.lottery import Lottery
from lightbulb import slash_commands
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import HAYATO_COLOR, LOTTERY_ICON
from utils.utils import get_author_name


@Lottery.subcommand()
class Balance(slash_commands.SlashSubCommand):
    description: str = 'Show your current credit balance.'
    enabled_guilds: list[int] = [705036924330704968]

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        await context.respond('Hold on a second...')
        author_name = get_author_name(context.author, context.member)
        participant = lottery_service.get_participant(int(context.author.id))
        if participant is None:
            await context.edit_response(content='You need to create an account by buying a lottery first!')
            return

        user_credit = await credit_service.get_user_credits(int(context.author.id), author_name, True)

        embed = hikari.Embed(title='Account Balance',
                             description='Here is your account balance.', color=HAYATO_COLOR)\
            .set_author(name=author_name, icon=context.author.avatar_url or context.author.default_avatar_url)\
            .set_thumbnail(LOTTERY_ICON)\
            .add_field(name='Credits', value=str(user_credit), inline=True)
        await context.edit_response(embed=embed, content='')
