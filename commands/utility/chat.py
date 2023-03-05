import lightbulb
import openai

from typing import Final
from services.configuration_service import configuration_service

TEXT_MODEL: Final[str] = 'gpt-3.5-turbo'
TEMPERATURE: Final[float] = 0.7
INITIAL_PROMPT: Final[str] = 'You are Hayasugi Hayato from the anime Shinkalion, and your responses will be energetic ' \
                             'and friendly, and should match the personality of Hayasugi Hayato.'


@lightbulb.option('prompt', 'The question you want to ask Hayato or anything you want to say.', required=True)
@lightbulb.command('chat', 'Hayato will chat with you or answer your questions with best efforts!', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def chat(ctx: lightbulb.Context) -> None:
    prompt: str = ctx.options.prompt
    openai.api_key = configuration_service.openai_api_key
    messages = [
        {'role': 'system', 'content': INITIAL_PROMPT},
        {'role': 'user', 'content': prompt}
    ]
    response = await openai.ChatCompletion.acreate(model=TEXT_MODEL, temperature=TEMPERATURE, messages=messages)

    if isinstance(response, list) or isinstance(response, dict):
        reply = extract(response)
        await ctx.respond(reply)
    else:
        try:
            reply = ''
            for obj in response:
                reply += extract(obj)
            await ctx.respond(reply)
        except Exception:
            await ctx.respond(str(response))


def extract(obj: list | dict) -> str:
    if isinstance(obj, list):
        reply = ''
        for inner_obj in obj:
            reply += inner_obj['choices'][0]['message']['content']
        return reply
    elif isinstance(obj, dict):
        return obj['choices'][0]['message']['content']
    else:
        return str(obj)
