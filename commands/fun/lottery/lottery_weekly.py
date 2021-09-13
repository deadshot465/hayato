import datetime

from commands.fun.lottery.lottery import Lottery
from lightbulb import slash_commands
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import TOTAL_SECONDS_PER_WEEK
from utils.utils import get_author_name


@Lottery.subcommand()
class Weekly(slash_commands.SlashSubCommand):
    description: str = 'Get your weekly credit!'
    enabled_guilds: list[int] = [705036924330704968]

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        await context.respond('Hold on a second...')
        author_name = get_author_name(context.author, context.member)
        participant = lottery_service.get_participant(int(context.author.id))
        if participant is None:
            await context.edit_response(content='You need to create an account by buying a lottery first!')
            return

        elapsed = datetime.datetime.now() - participant.last_weekly_time

        if elapsed.total_seconds() > TOTAL_SECONDS_PER_WEEK:
            await credit_service.add_credits(user_id=int(context.author.id),
                                             user_name=author_name,
                                             amount=70)
            participant.last_weekly_time = datetime.datetime.now()
            lottery_service.write_lottery()
            await context.edit_response(content='You have received your weekly 70 credits!')
        else:
            days = 7 - elapsed.total_seconds() / 60 / 60 / 24
            hours = (days - int(days)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            result = '%01d Days %02d:%02d:%02d' % (days, hours, minutes, seconds)
            await context.edit_response(content='You need to wait at least 7 days to receive the next weekly credits!'
                                                ' Time left: ' + result)
