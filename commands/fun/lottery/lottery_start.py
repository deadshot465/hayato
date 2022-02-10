import asyncio
import typing

import hikari
import lightbulb

from commands.fun.lottery.lottery import lottery
from services.lottery_service import lottery_service
from utils.constants import KOU_ADMIN_ROLE_ID


@lottery.child
@lightbulb.command('start', 'Manually start a lottery.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def start(ctx: lightbulb.Context) -> None:
    if lottery_service.lottery_running:
        await ctx.respond('There is already a lottery running now!')
        return

    starter = ctx.member
    if starter is None:
        await ctx.respond('The lottery can only be started in a guild channel!')
        return
    starter_roles = starter.get_roles()
    admin_role = (x for x in starter_roles if x.id == KOU_ADMIN_ROLE_ID)
    if next(admin_role, -1) == -1:
        await ctx.respond('The lottery can only be started by admins!')
        return

    await ctx.respond('The lottery will start in 10 seconds!')
    msg_generator = lottery_service.start_lottery()
    running_message = ''
    drawn_numbers: list[int] = []

    try:
        while True:
            s, i = await msg_generator.__anext__()
            running_message += s + '\n'
            drawn_numbers.append(i)
            await ctx.edit_last_response(content=running_message)
            await asyncio.sleep(3)
    except StopAsyncIteration:
        pass

    running_message += 'The drawn numbers are: ' + ''.join(str(drawn_numbers))
    await ctx.edit_last_response(content=running_message)

    msg_channel: typing.Optional[hikari.TextableGuildChannel] = ctx.get_channel()
    if msg_channel is None:
        return

    result_generator = lottery_service.build_lottery_result(drawn_numbers)

    try:
        while True:
            res = await result_generator.__anext__()
            if isinstance(res, hikari.Embed):
                await msg_channel.send(embed=res)
            else:
                await msg_channel.send(res)
            await asyncio.sleep(1.0)
    except StopAsyncIteration:
        return
