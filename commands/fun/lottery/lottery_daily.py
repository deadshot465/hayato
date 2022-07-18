import datetime

import arrow
import lightbulb
import logging
import requests

from commands.fun.lottery.lottery import lottery
from marshmallow_dataclass import class_schema
from services.authentication_service import AuthenticationService
from services.configuration_service import configuration_service
from services.lottery_service import lottery_service
from structures.lottery.user_lottery import UserLottery


@lottery.child
@lightbulb.command(name='daily', description='Get your daily credit!', auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def daily(ctx: lightbulb.Context) -> None:
    user_lottery = await lottery_service.get_user_lottery(int(ctx.author.id))
    if user_lottery is None:
        await ctx.respond(content='You need to create an account by buying a lottery first!')
        return

    AuthenticationService.login()
    headers = {
        'Authorization': f'Bearer {AuthenticationService.token}'
    }

    try:
        response = requests.get(configuration_service.api_endpoint + f'/lottery/{int(ctx.author.id)}/daily',
                                headers=headers)
        response.raise_for_status()
        status_code = response.status_code

        match status_code:
            case 200:
                await ctx.respond(content='You have received your daily 10 credits!')
            case 202:
                schema = class_schema(UserLottery)
                payload: UserLottery = schema().loads(json_data=response.text)

                next_daily_time = arrow.get(payload.next_daily_time).datetime
                remaining_time = next_daily_time - arrow.utcnow().datetime

                seconds_left = 86400 - remaining_time.seconds
                hours = seconds_left // 60 // 60
                leftover_sec = seconds_left - (hours * 60 * 60)
                minutes = leftover_sec // 60
                seconds = leftover_sec - (60 * minutes)
                result = '%02d:%02d:%02d' % (hours, minutes, seconds)
                await ctx.respond(content='You need to wait at least 24 hours to receive the next daily credits!'
                                          ' Time left: ' + result)
    except requests.exceptions.HTTPError as ex:
        error_message = f'Failed to get daily reward response: {ex.response}'
        logging.error(error_message)
        await ctx.respond(content=error_message)
        return
