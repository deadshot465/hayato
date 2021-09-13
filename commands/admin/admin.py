import hikari
from lightbulb import slash_commands
from services.configuration_service import configuration_service


class Admin(slash_commands.SlashCommandGroup):
    description: str = 'Administrative commands.'


@Admin.subcommand()
class Allow(slash_commands.SlashSubCommand):
    description: str = 'Allow a channel for Hayato\'s responses.'
    channel: hikari.TextableChannel = slash_commands.Option('The channel to allow responses.')

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        channel: hikari.TextableChannel = context.option_values.channel

        if int(channel) not in configuration_service.ignored_channels:
            await context.respond('The channel is not ignored!')
            return

        configuration_service.allow_channel(int(channel))
        await context.respond('Successfully allowed channel for responses!')


@Admin.subcommand()
class Ignore(slash_commands.SlashSubCommand):
    description: str = 'Disallow a channel for Hayato\'s responses.'
    channel: hikari.TextableChannel = slash_commands.Option('The channel to disallow responses.')

    async def callback(self, context: slash_commands.SlashCommandContext) -> None:
        channel: hikari.TextableChannel = context.option_values.channel

        if int(channel) in configuration_service.ignored_channels:
            await context.respond('The channel is already ignored!')
            return

        configuration_service.ignore_channel(int(channel))
        await context.respond('Successfully disallowed channel for responses!')
