from discord.ext import commands
from deprecated.commands.warnban.warnban import WarnBanData
from marshmallow import Schema
from dateutil.relativedelta import relativedelta
from typing import Optional, Union
from utils.deprecated.configuration_manager import ConfigurationManager
import asyncio
import datetime
import discord
import json
import marshmallow_dataclass
import re
import typing


# This regular expression is used to capture a channel tag/ping.
CHANNEL_TAG_REGEX = re.compile(r'<#(\d+)>')


async def add_warn(ctx: commands.Context, bot: commands.Bot, member: Union[discord.User, discord.Member], reason: str, warnban_data: typing.List[WarnBanData], schema: typing.Type[Schema]):
    author: Union[discord.User, discord.Member] = ctx.author
    embed = discord.Embed(title='Warn member', description='Are you sure you want to warn {}? Please confirm in 30 seconds.'.format(member.display_name), colour=discord.Colour.from_rgb(30, 99, 175))
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    embed.add_field(name='Reason', value=str(reason), inline=True)
    embed.set_footer(text="React with ✅ to confirm, react with ❌ to cancel.")
    sentembed: discord.Message = await ctx.send(embed=embed)
    await sentembed.add_reaction('✅')
    await sentembed.add_reaction('❌')

    def check(reaction: discord.Reaction, user):
        return user == ctx.author and reaction.message.id == sentembed.id and (
                    str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

    async def cancel():
        await ctx.message.delete()
        await sentembed.delete()
        await ctx.send('❌ The action is cancelled.')

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        # Timeout
        await cancel()
        return
    else:
        if reaction.emoji == '❌':
            await cancel()
            return
        else:
            user_data = list(filter(lambda x: x.user_id == member.id, warnban_data))
            user: WarnBanData
            if len(user_data) > 0:
                user = user_data[0]
                if user.username != member.display_name:
                    user.username = member.display_name
                user.warns += 1
                user.is_banned = False
                user.reasons.append(reason)
                if user.warns >= 3:
                    message = await add_ban(ctx, member, 30, 'Accumulated 3 warnings', warnban_data, schema)
                    await ctx.send(message)
                    return
                dm_channel: discord.DMChannel = await member.create_dm()
                await dm_channel.send('You are warned by {}. Reason: {}'.format(author.display_name, reason))
                serialized = schema().dumps(warnban_data, many=True)
                with open('assets/warnban.json', 'w') as file_1:
                    obj = json.loads(serialized)
                    file_1.write(json.dumps(obj, indent=2))
                return '{} is warned by {}. Reason: {}'.format(member.display_name, author.display_name, reason)
            else:
                user = WarnBanData(member.display_name, member.id, 1, False, datetime.datetime.now(),
                                   datetime.datetime.now(), list())
                user.reasons.append(reason)
                warnban_data.append(user)
                dm_channel: discord.DMChannel = await member.create_dm()
                await dm_channel.send('You are warned by {}. Reason: {}'.format(author.display_name, reason))
                serialized = schema().dumps(warnban_data, many=True)
                with open('assets/warnban.json', 'w') as file_1:
                    obj = json.loads(serialized)
                    file_1.write(json.dumps(obj, indent=2))
                return '{} is warned by {}. Reason: {}'.format(member.display_name, author.display_name, reason)


async def add_ban(ctx: commands.Context, bot: commands.Bot, member: Union[discord.User, discord.Member], time: int, reason: str, warnban_data: typing.List[WarnBanData], schema: typing.Type[Schema]):
    author: Union[discord.User, discord.Member] = ctx.author
    if time == -1:
        expiry = datetime.datetime.now() + relativedelta(years=1000)
    elif time == 0:
        await ctx.send('Please provide a valid time of banning in days.')
        return
    else:
        expiry = datetime.datetime.now() + relativedelta(days=time)
    embed = discord.Embed(title='Ban member',
                          description='Are you sure you want to ban {}? Please confirm in 30 seconds.'.format(member.display_name), colour=discord.Colour.from_rgb(30, 99, 175))
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    embed.add_field(name='Reason', value=str(reason), inline=True)
    embed.add_field(name='Ban Expiry Date', value=('{}-{}-{}'.format(expiry.year, expiry.month, expiry.day)))
    embed.set_footer(text="React with ✅ to confirm, react with ❌ to cancel.")
    sentembed: discord.Message = await ctx.send(embed=embed)
    await sentembed.add_reaction('✅')
    await sentembed.add_reaction('❌')

    def check(reaction: discord.Reaction, user):
        return user == ctx.author and reaction.message.id == sentembed.id and (
                str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

    async def cancel():
        await ctx.message.delete()
        await sentembed.delete()
        await ctx.send('❌ The action is cancelled.')

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        # Timeout
        await cancel()
        return
    else:
        if reaction.emoji == '❌':
            await cancel()
            return
        else:
            user_data = list(filter(lambda x: x.user_id == member.id, warnban_data))
            user: WarnBanData
            if len(user_data) > 0:
                user = user_data[0]
                if user.username != member.display_name:
                    user.username = member.display_name
                user.is_banned = True
                user.warns = 0
                user.ban_time = datetime.datetime.now()
                user.ban_expiry = expiry
                user.reasons.append(reason)
                await member.ban(reason=reason)
                dm_channel: discord.DMChannel = await member.create_dm()
                await dm_channel.send('You are banned by {} for {} days. Reason: {}\nBan expiry date: {}-{}-{}'.format(
                    author.display_name, time, reason, expiry.year, expiry.month, expiry.day))
                serialized = schema().dumps(warnban_data, many=True)
                with open('assets/warnban.json', 'w') as file_1:
                    obj = json.loads(serialized)
                    file_1.write(json.dumps(obj, indent=2))
                return '{} is banned by {} for {} days. Reason: {}\nBan expiry date: {}-{}-{}'.format(
                    member.display_name, author.display_name, time, reason, expiry.year, expiry.month, expiry.day)
            else:
                now = datetime.datetime.now()
                user = WarnBanData(member.display_name, member.id, 0, True, now, expiry, list())
                user.reasons.append(reason)
                warnban_data.append(user)
                await member.ban(reason=reason)
                dm_channel: discord.DMChannel = await member.create_dm()
                await dm_channel.send('You are banned by {} for {} days. Reason: {}\nBan expiry date: {}-{}-{}'.format(
                    author.display_name, time, reason, expiry.year, expiry.month, expiry.day))
                serialized = schema().dumps(warnban_data, many=True)
                with open('assets/warnban.json', 'w') as file_1:
                    obj = json.loads(serialized)
                    file_1.write(json.dumps(obj, indent=2))
                return '{} is banned by {} for {} days. Reason: {}\nBan expiry date: {}-{}-{}'.format(
                    member.display_name, author.display_name, time, reason, expiry.year, expiry.month, expiry.day)



class Admin(commands.Cog):
    warnban_schema = marshmallow_dataclass.class_schema(WarnBanData)
    with open('assets/warnban.json') as file_1:
        warnban_data: typing.List[WarnBanData] = warnban_schema().loads(json_data=file_1.read(), many=True)

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

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
        result = await add_warn(ctx, self.bot, member, reason, Admin.warnban_data, self.warnban_schema)
        if result is None:
            return
        await ctx.send(result)

    @commands.command(
        description='Bans a member. This command can can only be used by administrators.',
        help='Bans a member if he/she violated the rules seriously. This command can only be used by administrators.')
    async def ban(self, ctx: commands.Context, member: discord.Member, time: Optional[int] = 0, *, reason: Optional[str] = 'None'):
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            await ctx.send('Don\'t try to bypass admin rights. This is not a command for you to use.')
            return
        result = await add_ban(ctx, self.bot, member, time, reason, Admin.warnban_data, self.warnban_schema)
        if result is None:
            return
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
