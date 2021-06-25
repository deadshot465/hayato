import base64
import typing
import discord
import json
import os
import requests

from discord.ext import commands
from Utils.utils import PYTHON_LOGO, HAYATO_COLOR

SUBMISSION_URL = 'https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&fields=*'
PYTHON_LANG_ID = 71
RESULT_RAW_URL = 'https://judge0-ce.p.rapidapi.com/submissions/{token}?base64_encoded=true&fields=*'


def generate_auth_header(host: str) -> dict:
    api_key = os.getenv('RAPID_API_KEY')
    if api_key is None:
        return {}
    else:
        return {
            'content-type': 'application/json',
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': host
        }


async def get_eval_result(header: dict, token: str, ctx: commands.Context):
    result_url = RESULT_RAW_URL.replace('{token}', token)
    request = requests.request('GET', result_url, headers=header)
    print(f'{request.status_code}')
    response_body = json.loads(request.text)
    error_message = ''
    if response_body['stderr'] is not None and response_body['stderr'] != '':
        stderr = str(base64.b64decode(response_body['stderr'])).lstrip('b\'')
        error_message += f'An error occurred when evaluating your input! Error: **{stderr}**'
        if response_body['message'] is not None and response_body['message'] != '':
            message = str(base64.b64decode(response_body['message'])).lstrip('b\'')
            error_message += f'\nHere is an extra message for the error: **{message}**'
        if len(error_message) > 2000:
            error_message = error_message[:2000]
        await ctx.send(error_message)
        return True

    if request is None or response_body['stdout'] is None or response_body['stdout'] == '':
        return False

    author: typing.Union[discord.Member, discord.User] = ctx.author
    description = f'This is the evaluation result of {author.display_name}\'s Python code!\n'
    description += '```bash\n'
    description += str(base64.b64decode(response_body['stdout']).decode('utf-8')).lstrip('b\'') \
                       .replace('\\n', '\n').rstrip('\n\'') + '\n'
    description += '```'
    if len(description) > 2000:
        description = description[:2000]
    embed = discord.Embed(description=description, colour=HAYATO_COLOR)
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    embed.set_thumbnail(url=PYTHON_LOGO)
    embed.add_field(name='Time Spent', value='{} sec'.format(response_body['time']), inline=True)
    embed.add_field(name='Memory Spent', value='{} KB'.format(response_body['memory']), inline=True)

    if str(response_body['exit_code']) != '':
        embed.add_field(name='Exit Code', value=str(response_body['exit_code']), inline=True)
    if str(response_body['exit_signal']) != '':
        embed.add_field(name='Exit Signal', value=str(response_body['exit_signal']), inline=True)

    await ctx.send(embed=embed)
    return True
