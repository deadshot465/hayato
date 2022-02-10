import random
import typing

import lightbulb

__eightball_responses: typing.Final[list[str]] = \
        ['Of course', 'It is certain', 'I think so', 'Maybe', 'If you like Shinkansen, then yes',
         'I think this is as reliable as Shinkansen trains', 'This is as good as E5 Series',
         'Uhh...I am not sure', 'I don\'t want to tell you now, because I am watching Shinkalion now',
         'This question is like asking me if Shinkansen is rapid or not',
         'I am tired now, ask me later', 'Sorry, I don\'t know',
         'Think about it again and ask me later',
         'Definitely no', 'Of course no, don\'t ask me the same question again', 'I guess no',
         'Maybe not']


@lightbulb.option('question', 'The question you want to ask Hayato.', required=True)
@lightbulb.command(name='8ball', description='Get an answer from a yes/no question.')
@lightbulb.implements(lightbulb.SlashCommand)
async def eight_ball(ctx: lightbulb.Context) -> None:
    choice = random.choice(__eightball_responses)
    await ctx.respond('🎱 | {}, **{}**!'.format(choice, ctx.member.display_name))
