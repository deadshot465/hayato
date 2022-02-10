import random

import lightbulb


@lightbulb.option('choices', 'Choices to pick from, separated by comma (,).', required=True)
@lightbulb.command('pick', 'Hayato will help you pick one choice randomly.')
@lightbulb.implements(lightbulb.SlashCommand)
async def pick(ctx: lightbulb.Context) -> None:
    choices: str = ctx.options.choices
    all_choices = [s.strip() for s in choices.split(',') if s.strip() != '']
    hayato_choice = random.choice(all_choices)

    await ctx.respond('I pick **%s** for you!' % hayato_choice)
