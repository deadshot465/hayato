import datetime

import lightbulb

from commands.fun.lottery.lottery import lottery
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import TOTAL_SECONDS_PER_WEEK
from utils.utils import get_author_name


@lottery.child
@lightbulb.command('weekly', 'Get your weekly credit!', auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def weekly(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    participant = lottery_service.get_participant(int(ctx.author.id))
    if participant is None:
        await ctx.respond(content='You need to create an account by buying a lottery first!')
        return

    elapsed = datetime.datetime.now() - participant.last_weekly_time

    if elapsed.total_seconds() > TOTAL_SECONDS_PER_WEEK:
        await credit_service.add_credits(user_id=int(ctx.author.id),
                                         user_name=author_name,
                                         amount=70)
        participant.last_weekly_time = datetime.datetime.now()
        lottery_service.write_lottery()
        await ctx.respond(content='You have received your weekly 70 credits!')
    else:
        days = 7 - elapsed.total_seconds() / 60 / 60 / 24
        hours = (days - int(days)) * 24
        minutes = (hours - int(hours)) * 60
        seconds = (minutes - int(minutes)) * 60
        result = '%01d Days %02d:%02d:%02d' % (days, hours, minutes, seconds)
        await ctx.respond(content='You need to wait at least 7 days to receive the next weekly credits!'
                                  ' Time left: ' + result)
