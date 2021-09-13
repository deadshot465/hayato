import asyncio
import typing

from lightbulb.context import Context

from services.configuration_service import configuration_service
from services.judge_zero_service import judge_zero_service
from utils.utils import get_author_name


# Currently it's not possible to send multi-lined strings to slash commands.
@configuration_service.bot.command(name='eval', aliases=['evaluate'])
async def evaluate(ctx: Context):
    msg_content = ctx.content
    code_block_start_index = msg_content.index('`')
    code_block_text = msg_content[code_block_start_index:]\
        .split('\n')[1:-1]
    code_block = '\n'.join(code_block_text)

    token = judge_zero_service.create_eval_request(code_block)
    if token is None:
        await ctx.respond('Sorry, I can\'t seem to send the request!')
        return

    eval_task: asyncio.Task[typing.Optional[dict]] =\
        asyncio.create_task(judge_zero_service.try_get_eval_result(token))

    eval_result = await eval_task
    if eval_result is None:
        await ctx.respond('Uhh...I\'ve tried many times but I can\'t seem to get anything for you... :(')
    else:
        stderr = eval_result.get('stderr')
        message = eval_result.get('message')
        error_msg = ''

        if stderr is not None or message is not None:
            if stderr != '':
                error_msg += 'Sorry, I can\'t evaluate your code because there\'s something wrong!\n\n'
                error_msg += 'Here is the error message: **%s**\n\n' % stderr
            if message != '':
                error_msg += 'Here are some extra messages for you: **%s**\n\n' % message
            await ctx.respond(error_msg[:2000])

        else:
            author_name = get_author_name(ctx.author, ctx.member)
            embed = judge_zero_service.build_embed(eval_result, author_name,
                                                   ctx.author.avatar_url or ctx.author.default_avatar_url)
            await ctx.respond(embed=embed)
