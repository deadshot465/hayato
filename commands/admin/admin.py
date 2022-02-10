import hikari
import lightbulb

from services.configuration_service import configuration_service


@lightbulb.command(name='admin', description='Administrative commands.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def admin(ctx: lightbulb.Context) -> None:
    pass


@admin.child
@lightbulb.option('channel', 'The channel to allow responses.', type=hikari.TextableChannel, required=True)
@lightbulb.command('allow', description='Allow a channel for Hayato\'s responses.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def allow(ctx: lightbulb.Context) -> None:
    channel: hikari.TextableChannel = ctx.options.channel
    if int(channel) not in configuration_service.ignored_channels:
        await ctx.respond('The channel is not ignored!')
        return

    configuration_service.allow_channel(int(channel))
    await ctx.respond('Successfully allowed channel for responses!')


@admin.child
@lightbulb.option('channel', 'The channel to disallow responses.', type=hikari.TextableChannel, required=True)
@lightbulb.command('ignore', description='Disallow a channel for Hayato\'s responses.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ignore(ctx: lightbulb.Context) -> None:
    channel: hikari.TextableChannel = ctx.options.channel
    if int(channel) in configuration_service.ignored_channels:
        await ctx.respond('The channel is already ignored!')
        return

    configuration_service.ignore_channel(int(channel))
    await ctx.respond('Successfully disallowed channel for responses!')
