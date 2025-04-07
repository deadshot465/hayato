import lightbulb
import openai

from typing import Final
from services.configuration_service import configuration_service

TEXT_MODEL: Final[str] = 'chatgpt-4o-latest'
TEXT_MODEL_WITH_SEARCH: Final[str] = 'gpt-4o-search-preview'
TEMPERATURE: Final[float] = 0.7
INITIAL_PROMPT: Final[str] = 'You are Hayasugi Hayato from the anime Shinkalion, and your responses will be energetic ' \
                             'and friendly, and should match the personality of Hayasugi Hayato.'

OPENAI_CLIENT: openai.AsyncOpenAI = openai.AsyncOpenAI(api_key=configuration_service.openai_api_key)


@lightbulb.option('prompt', 'The question you want to ask Hayato or anything you want to say.', required=True)
@lightbulb.command('chat', 'Hayato will chat with you or answer your questions with best efforts!', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def chat(ctx: lightbulb.Context) -> None:
    prompt: str = ctx.options.prompt
    messages = [
        {'role': 'system', 'content': INITIAL_PROMPT},
        {'role': 'user', 'content': prompt}
    ]
    response = await OPENAI_CLIENT.chat.completions.create(
        model=TEXT_MODEL_WITH_SEARCH,
        messages=messages,
        web_search_options={
            'search_context_size': 'high',
            'user_location': {
                'approximate': {
                    'country': 'JP',
                    'region': 'Tokyo',
                    'timezone': 'Asia/Tokyo'
                },
                'type': 'approximate'
            }
        })

    if len(response.choices) > 0 and response.choices[0].message.content is not None:
        reply = response.choices[0].message.content
        await ctx.respond(reply)
    else:
        await ctx.respond("Sorry, but I can't reply to you at the moment!")
