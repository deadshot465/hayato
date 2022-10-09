import hikari
import lightbulb
import logging

from services.configuration_service import configuration_service
from services.google_api_service import upload


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

@admin.child
@lightbulb.command('Save to Tetsu\'s Google Drive', '', auto_defer=True)
@lightbulb.implements(lightbulb.MessageCommand)
async def save_to_drive(ctx: lightbulb.Context) -> None:
    results = []
    messages = ctx.resolved.messages
    for message in messages.values():
        attachments = message.attachments
        for attachment in attachments:
            logging.info(f'Reading file: {attachment.filename}...')
            raw_bytes = await attachment.read()
            result = await upload(raw_bytes)
            results.append(result)
    if False in results:
        await ctx.respond('Some uploads failed. Check the error log!')
    else:
        await ctx.respond('All uploads completed!')
