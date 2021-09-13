import datetime
import discord
import googlemaps
import json
import os
import random
import requests
import time as _time
import typing

from discord.ext import commands
from utils.utils import PYTHON_LOGO, HAYATO_COLOR

GOOGLE_ENDPOINT = 'https://maps.googleapis.com/maps/api/timezone/{}?{}'
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.pings = ['Pong', 'Pang', 'Peng', 'Pung']

    @commands.command(description='See the information about Hayato.',
                      help='The information about Hayato, e.g. authors, version number, etc.', aliases=['credits'])
    async def about(self, ctx: commands.Context):
        avatar_url = str(self.bot.user.avatar_url)
        embed = discord.Embed(color=HAYATO_COLOR,
                              description='Hayato the best boi is inspired by the anime Shinkalion. It is meant for '
                                          'practising making a Discord bot in [Python](https://www.python.org/) with '
                                          'the awesome [discord.py](https://github.com/Rapptz/discord.py), '
                                          'but new features will be '
                                          'added from time to time.\n\nHayato version 2.4.3 was made and developed '
                                          'by:\n**Kirito#9286** and **Tetsuki Syu#1250**\nHayato Bot is licensed '
                                          'under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html').set_footer(
            text='Hayato Bot: Release 2.4.3 | 2021-06-26').set_author(name='Hayasugi Hayato from Shinkalion',
                                                                      icon_url=avatar_url).set_thumbnail(
            url=PYTHON_LOGO)
        await ctx.send(embed=embed)

    @commands.command(description='Play a ping-pong message with Hayato and check if Hayato is fine.',
                      help='Send a simple ping command to Hayato and get response.', aliases=['pong'])
    async def ping(self, ctx: commands.Context):
        start_time = datetime.datetime.now()
        bot: discord.ext.commands.Bot = ctx.bot
        message = await ctx.send('🏓 Pinging...')
        end_time = datetime.datetime.now()
        elapsed = round((end_time - start_time).total_seconds() * 1000, 3)
        heartbeat_latency: float = bot.latency
        await message.edit(
            content='🏓 {}!\nLatency is: {}ms. Heartbeat latency is: {}ms.'.format(random.choice(self.pings), elapsed,
                                                                                   round(heartbeat_latency * 1000, 3)))

    @commands.command(description='Get the current time of an arbitrary timezone.',
                      help='Get the current time in an arbitrary timezone. The queried timezone has to be a valid timezone officially registered.',
                      aliases=['watch'])
    async def time(self, ctx: commands.Context, *, args: typing.Optional[str] = ''):
        if len(args) == 0 or args == '':
            await ctx.send('I need a keyword to search for the timezone!')
            return
        response = requests.get(url='http://worldtimeapi.org/api/timezone/')
        time_zone_list: typing.List[str] = json.loads(response.text)
        args = args.lower().replace(' ', '_')
        time_zone_name = ''
        for time_zone in time_zone_list:
            if args in time_zone.lower():
                time_zone_name = time_zone
                break
        if time_zone_name == '':
            try:
                geocode = gmaps.geocode(args)
                item: dict = geocode[0]
                geometry: dict = item['geometry']
                location: dict = geometry['location']
                actual_location = (location['lat'], location['lng'])
                time_zone_data: dict = gmaps.timezone(actual_location, _time.time())
                time_zone_name = time_zone_data['timeZoneId']
            except:
                await ctx.send('Sorry, I don\'t know the time of this city!')
                return
        response = requests.get(url='http://worldtimeapi.org/api/timezone/' + time_zone_name)
        time_info = json.loads(response.text)
        time_string: str = time_info['datetime']
        time = datetime.datetime.fromisoformat(time_string)
        await ctx.send('The local time of **' + time_zone_name.replace('_', ' ') + '** is ' + time.strftime(
            '%Y-%m-%d %H:%M:%S') + '!')

    @commands.command(description='Get the information about this server.',
                      help='Get detailed information about this server, including the owner, etc.', aliases=['server'])
    async def guild(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        author: typing.Union[discord.User, discord.Member] = ctx.author
        embed = discord.Embed(title='Server Information',
                              description=f'Here is the detailed information of {guild.name}.', color=HAYATO_COLOR)
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.set_thumbnail(url=guild.icon_url)
        if guild.banner is not None:
            embed.add_field(name='Banner', value=guild.banner, inline=False)
        if guild.banner_url is not None and len(str(guild.banner_url)) > 0:
            embed.add_field(name='Banner URL', value=str(guild.banner_url), inline=False)
        embed.add_field(name='Creation Date', value=guild.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        if guild.description is not None:
            embed.add_field(name='Description', value=guild.description, inline=False)
        if len(guild.features) > 0:
            embed.add_field(name='Features', value=(', '.join(guild.features)), inline=False)
        embed.add_field(name='Guild ID', value=guild.id, inline=False)
        embed.add_field(name='Owner',
                        value='{}#{} [{}]'.format(guild.owner.display_name, guild.owner.discriminator, guild.owner.id),
                        inline=False)
        if guild.splash is not None:
            embed.add_field(name='Splash', value=guild.splash, inline=False)
        if guild.splash_url is not None and len(str(guild.splash_url)) > 0:
            embed.add_field(name='Splash URL', value=str(guild.splash_url), inline=False)
        embed.add_field(name='Emoji Limits', value=guild.emoji_limit, inline=True)
        embed.add_field(name='File Size Limits', value=guild.filesize_limit, inline=True)
        embed.add_field(name='Members', value=guild.member_count, inline=True)
        embed.add_field(name='Voice Region', value=str(guild.region), inline=True)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
