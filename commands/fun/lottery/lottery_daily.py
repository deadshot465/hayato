import datetime

import lightbulb

from commands.fun.lottery.lottery import lottery
from services.credit_service import credit_service
from services.lottery_service import lottery_service
from utils.constants import TOTAL_SECONDS_PER_DAY
from utils.utils import get_author_name


@lottery.child
@lightbulb.command(name='daily', description='Get your daily credit!', auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def daily(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    participant = lottery_service.get_participant(int(ctx.author.id))
    if participant is None:
        await ctx.respond(content='You need to create an account by buying a lottery first!')
        return

    elapsed = datetime.datetime.now() - participant.last_daily_time

    if elapsed.total_seconds() > TOTAL_SECONDS_PER_DAY:
        await credit_service.add_credits(user_id=int(ctx.author.id),
                                         user_name=author_name,
                                         amount=10)
        participant.last_daily_time = datetime.datetime.now()
        lottery_service.write_lottery()
        await ctx.respond(content='You have received your daily 10 credits!')
    else:
        seconds_left = 86400 - elapsed.seconds
        hours = seconds_left // 60 // 60
        leftover_sec = seconds_left - (hours * 60 * 60)
        minutes = leftover_sec // 60
        seconds = leftover_sec - (60 * minutes)
        result = '%02d:%02d:%02d' % (hours, minutes, seconds)
        await ctx.respond(content='You need to wait at least 24 hours to receive the next daily credits!'
                                  ' Time left: ' + result)
