import lightbulb


@lightbulb.command(name='lottery', description='Wanna try your luck?')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def lottery(ctx: lightbulb.Context) -> None:
    pass
