import random

from lightbulb import slash_commands


class Pick(slash_commands.SlashCommand):
    description: str = 'Hayato will help you pick one choice randomly.'
    choices: str = slash_commands.Option('Choices to pick from, separated by comma (,).')

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        choices: str = context.option_values.choices
        all_choices = [s.strip() for s in choices.split(',') if s.strip() != '']
        hayato_choice = random.choice(all_choices)

        await context.respond('I pick **%s** for you!' % hayato_choice)
