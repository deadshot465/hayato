from discord.ext import commands
from Include.Commands.warnban.warnban import WarnBanData
from marshmallow import Schema
from typing import Optional, Union
from Utils.configuration_manager import ConfigurationManager
import datetime
import discord
import json
import marshmallow_dataclass
import re
import typing


# This regular expression is used to capture a channel tag/ping.
CHANNEL_TAG_REGEX = re.compile(r'<#(\d+)>')


async def add_warn(ctx: commands.Context, member: Union[discord.User, discord.Member], reason: str, warnban_data: typing.List[WarnBanData], schema: typing.Type[Schema]):
    author: Union[discord.User, discord.Member] = ctx.author
    user_data = list(filter(lambda x: x.user_id == member.id, warnban_data))
    user: WarnBanData
    if len(user_data) > 0:
        user = user_data[0]
        if user.username != member.display_name:
            user.username = member.display_name
        user.warns += 1
        user.reasons.append(reason)
        serialized = schema().dumps(warnban_data, many=True)
        with open('Storage/warnban.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return '{} is warned by {}. Reason: {}'.format(member.display_name, author.display_name, reason)
    else:
        user = WarnBanData(member.display_name, member.id, 1, False, datetime.datetime.now(), datetime.datetime.now(), list())
        user.reasons.append(reason)
        warnban_data.append(user)
        serialized = schema().dumps(warnban_data, many=True)
        with open('Storage/warnban.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return '{} is warned by {}. Reason: {}'.format(member.display_name, author.display_name, reason)


async def add_ban(ctx: commands.Context, member: Union[discord.User, discord.Member], time: int, reason: str, warnban_data: typing.List[WarnBanData], schema: typing.Type[Schema]):
    author: Union[discord.User, discord.Member] = ctx.author
    user_data = list(filter(lambda x: x.user_id == member.id, warnban_data))
    user: WarnBanData
    if len(user_data) > 0:
        user = user_data[0]
        if user.username != member.display_name:
            user.username = member.display_name
        user.is_banned = True
        user.warns = 0
        user.ban_time = datetime.datetime.now()
        user.reasons.append(reason)
        # await member.ban(reason=reason)
        serialized = schema().dumps(warnban_data, many=True)
        with open('Storage/warnban.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return '{} is banned by {}. Reason: {}'.format(member.display_name, author.display_name, reason)
    else:
        user = WarnBanData(member.display_name, member.id, 0, True, datetime.datetime.now(), datetime.datetime.now(),
                           list())
        user.reasons.append(reason)
        warnban_data.append(user)
        # await member.ban(reason=reason)
        serialized = schema().dumps(warnban_data, many=True)
        with open('Storage/warnban.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return '{} is banned by {}. Reason: {}'.format(member.display_name, author.display_name, reason)


class Admin(commands.Cog):
    warnban_schema = marshmallow_dataclass.class_schema(WarnBanData)
    with open('Storage/warnban.json') as file_1:
        warnban_data: typing.List[WarnBanData] = warnban_schema().loads(json_data=file_1.read(), many=True)

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
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = 'None'):
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            await ctx.send('Don\'t try to bypass admin rights. This is not a command for you to use.')
            return
        result = await add_warn(ctx, member, reason, Admin.warnban_data, self.warnban_schema)
        await ctx.send(result)

    async def ban(self, ctx: commands.Context, member: discord.Member, time: Optional[int] = 0, *, reason: Optional[str] = 'None'):
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            await ctx.send('Don\'t try to bypass admin rights. This is not a command for you to use.')
            return
        result = await add_ban(ctx, member, time, reason, Admin.warnban_data, self.warnban_schema)
        await ctx.send(result)

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
