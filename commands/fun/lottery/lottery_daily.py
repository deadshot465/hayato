import datetime

from commands.fun.lottery.lottery import Lottery
from lightbulb import slash_commands
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import TOTAL_SECONDS_PER_DAY
from utils.utils import get_author_name


@Lottery.subcommand()
class Daily(slash_commands.SlashSubCommand):
    description: str = 'Get your daily credit!'
    enabled_guilds: list[int] = [705036924330704968]

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        await context.respond('Hold on a second...')
        author_name = get_author_name(context.author, context.member)
        participant = lottery_service.get_participant(int(context.author.id))
        if participant is None:
            await context.edit_response(content='You need to create an account by buying a lottery first!')
            return

        elapsed = datetime.datetime.now() - participant.last_daily_time

        if elapsed.total_seconds() > TOTAL_SECONDS_PER_DAY:
            await credit_service.add_credits(user_id=int(context.author.id),
                                             user_name=author_name,
                                             amount=10)
            participant.last_daily_time = datetime.datetime.now()
            lottery_service.write_lottery()
            await context.edit_response(content='You have received your daily 10 credits!')
        else:
            seconds_left = 86400 - elapsed.seconds
            hours = seconds_left // 60 // 60
            leftover_sec = seconds_left - (hours * 60 * 60)
            minutes = leftover_sec // 60
            seconds = leftover_sec - (60 * minutes)
            result = '%02d:%02d:%02d' % (hours, minutes, seconds)
            await context.edit_response(content='You need to wait at least 24 hours to receive the next daily credits!'
                                                ' Time left: ' + result)
