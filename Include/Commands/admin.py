from discord.ext import commands
from typing import Dict, List, Optional, Set, Union
import discord
import json
import re


# This regular expression is used to capture a channel tag/ping.
CHANNEL_TAG_REGEX = re.compile(r'<#(\d+)>')
FILE_PATH = 'Storage/channels.json'


class Admin(commands.Cog):
    # Instead of admin1.channel_settings and admin2.channel_settings
    # We would have Admin.channel_settings, because it belongs to the "Admin" class itself.
    with open(FILE_PATH, 'r', encoding='utf-8') as file_1:
        raw_channel_settings = file_1.read()
        channel_settings: Dict[str, List[int]] = json.loads(raw_channel_settings)
        if channel_settings.get('enabled_channels') is None:
            channel_settings['enabled_channels'] = list()

    def __init__(self, bot: commands.Bot):
        super().__init__()

    @commands.command()
    async def enable(self, ctx: commands.Context, *, args: Optional[str] = None):
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            return
        # Similar to if len(args) = 0 or args == ''
        if args is None:
            await ctx.send('You need to provide a channel for me to enable!')
            return
        # h!enable Q!!!((
        if CHANNEL_TAG_REGEX.match(args) is None:
            await ctx.send('The channel tag you provided is invalid!')
            return
        channel_id = CHANNEL_TAG_REGEX.match(args).group(1)
        if int(channel_id) in Admin.channel_settings['enabled_channels']:
            await ctx.send('The channel is already enabled!')
            return
        else:
            Admin.channel_settings['enabled_channels'].append(int(channel_id))
            await ctx.send('Successfully enabled the channel {}!'.format(CHANNEL_TAG_REGEX.match(args).group(0)))
        with open(FILE_PATH, 'w') as file_1:
            raw_string = json.dumps(Admin.channel_settings, indent=2)
            file_1.write(raw_string)


    @commands.command()
    async def disable(self, ctx: commands.Context, *, args: Optional[str] = None):
        author: Union[discord.User, discord.Member] = ctx.author
        permission: discord.Permissions = author.permissions_in(ctx.channel)
        is_administrator = permission.administrator
        if not is_administrator:
            return
        if args is None:
            await ctx.send('You need to provide a channel for me to disable!')
            return
        if CHANNEL_TAG_REGEX.match(args) is None:
            await ctx.send('The channel tag you provided is invalid!')
            return
        channel_id = CHANNEL_TAG_REGEX.match(args).group(1)
        if int(channel_id) not in Admin.channel_settings['enabled_channels']:
            await ctx.send('The channel is not yet enabled!')
            return
        else:
            Admin.channel_settings['enabled_channels'].remove(int(channel_id))
            await ctx.send('Successfully disabled the channel {}!'.format(CHANNEL_TAG_REGEX.match(args).group(0)))
        with open(FILE_PATH, 'w') as file_1:
            raw_string = json.dumps(Admin.channel_settings, indent=2)
            file_1.write(raw_string)


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
