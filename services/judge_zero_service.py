import asyncio
import base64
import logging
import typing
import discord
import json
import os
import requests

import hikari
from services.configuration_service import configuration_service
from utils.constants import HAYATO_COLOR, PYTHON_LOGO


class JudgeZeroService:
    _submission_url: typing.Final[str] = 'https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&fields=*'
    _python_lang_id: typing.Final[int] = 71
    _result_raw_url: typing.Final[
        str] = 'https://judge0-ce.p.rapidapi.com/submissions/{token}?base64_encoded=true&fields=*'
    _host: typing.Final[str] = 'judge0-ce.p.rapidapi.com'
    _query_string: typing.Final[dict[str, str]] = {
        'base64_encoded': 'true',
        'fields': '*'
    }
    _default_max_attempt: typing.Final[int] = 10

    @staticmethod
    def build_embed(response: dict, author_name: str, author_avatar_url: str) -> hikari.Embed:
        description = f'This is the evaluation result of {author_name}\'s Python code!\n'
        description += '```bash\n'
        description += str(base64.b64decode(response['stdout']).decode('utf-8')).lstrip('b\'') \
                           .replace('\\n', '\n').rstrip('\n\'') + '\n'
        description += '```'
        embed = hikari.Embed(color=HAYATO_COLOR, description=description[:2000])\
            .set_author(name=author_name, icon=author_avatar_url)\
            .set_thumbnail(PYTHON_LOGO)\
            .add_field('Time Spent', '{} sec'.format(response['time']), inline=True)\
            .add_field('Memory Spent', '{} KB'.format(response['memory']), inline=True)

        exit_code = response.get('exit_code')
        exit_signal = response.get('exit_signal')
        if exit_code is not None and exit_code != '':
            embed.add_field(name='Exit Code', value=str(exit_code), inline=True)
        if exit_signal is not None and exit_signal != '':
            embed.add_field(name='Exit Signal', value=str(exit_signal), inline=True)
        return embed

    def create_eval_request(self, code_block: str) -> typing.Optional[str]:
        header = self.__generate_auth_header(self._host)
        request_data = self.__build_request_data(code_block)
        request = requests.request('POST', self._submission_url, headers=header, data=json.dumps(request_data),
                                   params=self._query_string)
        try:
            request.raise_for_status()
        except requests.HTTPError as e:
            logging.error(e)
            logging.error('Eval request failed.')
            return

        return json.loads(request.text)['token']

    async def try_get_eval_result(self, token: str) -> typing.Optional[dict]:
        initial_result = self.__get_eval_result(token)
        if initial_result is None:
            for _ in range(0, self._default_max_attempt):
                await asyncio.sleep(2.0)
                result = self.__get_eval_result(token)
                if result is not None:
                    return result
        return initial_result

    def __build_request_data(self, code_block: str):
        return {
            'language_id': self._python_lang_id,
            'source_code': str(base64.b64encode(code_block.encode('utf8'))).lstrip('b\'')
        }

    @staticmethod
    def __generate_auth_header(host: str) -> dict[str, str]:
        api_key = configuration_service.rapid_api_key
        return {
            'content-type': 'application/json',
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': host
        }

    def __get_eval_result(self, token: str) -> typing.Optional[dict]:
        result_url = self._result_raw_url.replace('{token}', token)
        request = requests.request('GET', result_url, headers=self.__generate_auth_header(self._host))
        try:
            request.raise_for_status()
        except requests.HTTPError as e:
            logging.error(e)
            return None

        response: dict = json.loads(request.text)
        response = self.__handle_error(response)
        stderr: typing.Optional[str] = response.get('stderr')
        message: typing.Optional[str] = response.get('message')
        if (stderr is not None and stderr != '') or (message is not None and message != ''):
            return response

        stdout: typing.Optional[str] = response.get('stdout')
        if stdout is None or stdout == '':
            return None

        return response

    @staticmethod
    def __handle_error(response: dict) -> dict:
        stderr: typing.Optional[str] = response.get('stderr')
        message: typing.Optional[str] = response.get('message')
        error_result: dict[str, str] = dict()
        if stderr is not None and stderr != '':
            error_result['stderr'] = str(base64.b64decode(stderr)).lstrip('b\'')
        if message is not None and message != '':
            error_result['message'] = str(base64.b64decode(message)).lstrip('b\'')

        if len(error_result) == 0:
            return response
        else:
            response['stderr'] = error_result.get('stderr')
            response['message'] = error_result.get('message')
            return response


judge_zero_service = JudgeZeroService()
