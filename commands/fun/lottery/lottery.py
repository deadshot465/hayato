from lightbulb import slash_commands


class Lottery(slash_commands.SlashCommandGroup):
    description: str = 'Wanna try your luck?'
    enabled_guilds: list[int] = [705036924330704968]
