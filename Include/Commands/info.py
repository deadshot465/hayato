import datetime
import discord
import json
import random
import requests
import typing
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.pings = ['pong', 'pang', 'peng', 'pung']

    @commands.command(description='See the information about Hayato.', help='The information about Hayato, e.g. authors, version number, etc.', aliases=['credits'])
    async def about(self, ctx: commands.Context):
        avatar_url = str(self.bot.user.avatar_url)
        embed = discord.Embed(color=discord.Color.from_rgb(30, 99, 175),
                              description='Hayato the best boi is inspired by the anime Shinkalion. It is meant for '
                                          'practising making a Discord bot in [Python](https://www.python.org/) with the awesome [discord.py](https://github.com/Rapptz/discord.py), but new features will be '
                                          'added from time to time.\n\nHayato version 2.1 was made and developed '
                                          'by:\n**Kirito#9286** and **Tetsuki Syu#1250**\nHayato Bot is licensed '
                                          'under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html').set_footer(
            text='Hayato Bot: Release 2.2 | 2020-08-09').set_author(name='Hayasugi Hayato from Shinkalion',
                                                                    icon_url=avatar_url).set_thumbnail(
            url='https://pbs.twimg.com/profile_images/1245939758695510016/UOG9MGdU_400x400.png')
        await ctx.send(embed=embed)

    @commands.command(description='Play a ping-pong message with Hayato and check if Hayato is fine.', help='Send a simple ping command to Hayato and get response.', aliases=['pong'])
    async def ping(self, ctx: commands.Context):
        await ctx.send(random.choice(self.pings))

    @commands.command(description='Get the current time of an arbitrary timezone.', help='Get the current time in an arbitrary timezone. The queried timezone has to be a valid timezone officially registered.', aliases=['watch'])
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
            await ctx.send('Sorry, I don\'t know the time of this city!')
            return
        response = requests.get(url='http://worldtimeapi.org/api/timezone/' + time_zone_name)
        time_info = json.loads(response.text)
        time_string: str = time_info['datetime']
        time = datetime.datetime.fromisoformat(time_string)
        await ctx.send('The local time of **' + time_zone_name.replace('_', ' ') + '** is ' + time.strftime('%Y-%m-%d %H:%M:%S') + '!')


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
