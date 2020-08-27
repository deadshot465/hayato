from discord.ext import commands
from typing import Optional, Union
from Utils.configuration_manager import ConfigurationManager
import discord
import re


# This regular expression is used to capture a channel tag/ping.
CHANNEL_TAG_REGEX = re.compile(r'<#(\d+)>')


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()

    @commands.command(description='Enable a channel for Hayato usage. This command can only be used by administrators.', help='Disable a channel for bot usage. All commands can only be executed in enabled channels. This command can only be used by administrators.')
    async def enable(self, ctx: commands.Context, *, args: Optional[str] = None):
        if (await self.validate(ctx, args)) is False:
            return
        channel_id = CHANNEL_TAG_REGEX.match(args).group(1)
        if int(channel_id) in ConfigurationManager.get_available_channels():
            await ctx.send('The channel is already enabled!')
            return
        else:
            ConfigurationManager.update_channel('enable', int(channel_id))
            await ctx.send('Successfully enabled the channel {}!'.format(CHANNEL_TAG_REGEX.match(args).group(0)))

    @commands.command(description='Disable a channel for Hayato usage. This command can only be used by administrators.', help='Disable a channel for bot usage. All commands can only be executed in enabled channels. This command can only be used by administrators.')
    async def disable(self, ctx: commands.Context, *, args: Optional[str] = None):
        if (await self.validate(ctx, args)) is False:
            return
        channel_id = CHANNEL_TAG_REGEX.match(args).group(1)
        if int(channel_id) not in ConfigurationManager.get_available_channels():
            await ctx.send('The channel is not yet enabled!')
            return
        else:
            ConfigurationManager.update_channel('disable', int(channel_id))
            await ctx.send('Successfully disabled the channel {}!'.format(CHANNEL_TAG_REGEX.match(args).group(0)))

    @commands.command(
        description='Disable a channel for Hayato replies. This command can only be used by administrators.',
        help='Disable a channel for Hayato replies. Hayato won\'t reply in ignored channels. This command can only be used by administrators.')
    async def ignore(self, ctx: commands.Context, *, args: Optional[str] = None):
        if (await self.validate(ctx, args)) is False:
            return
        channel_id = CHANNEL_TAG_REGEX.match(args).group(1)
        if int(channel_id) in ConfigurationManager.get_ignored_channels():
            await ctx.send('The channel is already ignored!')
            return
        else:
            ConfigurationManager.update_channel('ignore', int(channel_id))
            await ctx.send('Successfully ignored the channel {}!'.format(CHANNEL_TAG_REGEX.match(args).group(0)))

    @commands.command(
        description='Enable a channel for Hayato replies. This command can only be used by administrators.',
        help='Enable a channel for Hayato replies. Hayato won\'t reply in ignored channels. This command can only be used by administrators.')
    async def allow(self, ctx: commands.Context, *, args: Optional[str] = None):
        if (await self.validate(ctx, args)) is False:
            return
        channel_id = CHANNEL_TAG_REGEX.match(args).group(1)
        if int(channel_id) not in ConfigurationManager.get_ignored_channels():
            await ctx.send('The channel is not ignored!')
            return
        else:
            ConfigurationManager.update_channel('allow', int(channel_id))
            await ctx.send('Successfully allowed the channel {}!'.format(CHANNEL_TAG_REGEX.match(args).group(0)))

    @commands.command(
        description='Warns a member. This command can can only be used by administrators.',
        help='Warns a member if he/she violated the rules. This command can only be used by administrators.')
    async def warn(self, ctx: commands.Context, member, reason: Optional[str] = 'None'):
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            await ctx.send('Don\'t try to bypass admin rights. This is not a command for you to use.')
            return
        await ctx.send('This command is not implemented yet.')

    # Validate inputs.
    # Return true if the input is valid.
    @staticmethod
    async def validate(ctx: commands.Context, args: Optional[str]) -> bool:
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            return False
        if args is None:
            await ctx.send('You need to provide a channel for me to enable/disable!')
            return False
        if CHANNEL_TAG_REGEX.match(args) is None:
            await ctx.send('The channel tag you provided is invalid!')
            return False
        return True


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
