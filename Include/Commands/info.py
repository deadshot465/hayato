import discord
import random
from discord.ext import commands


class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.pings = ['pong', 'pang', 'peng', 'pung']

    @commands.command()
    async def about(self, ctx: commands.Context):
        avatar_url = str(self.bot.user.avatar_url)
        embed = discord.Embed(color=discord.Color.from_rgb(30, 99, 175),
                              description='Hayato the best boi is inspired by the anime Shinkalion. It is meant for '
                                          'practising making a Discord bot in Discord.py, but new features will be '
                                          'added from time to time.\n\nHayato version 1.0 was made and developed '
                                          'by:\n**Kirito#9286** and **Tetsuki Syu#1250**\nHayato Bot is licensed '
                                          'under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html').set_footer(
            text='Hayato Bot: Release 1.1 | 2020-08-01').set_author(name='Hayasugi Hayato from Shinkalion',
                                                                    icon_url=avatar_url).set_thumbnail(
            url='https://pbs.twimg.com/profile_images/1245939758695510016/UOG9MGdU_400x400.png')
        await ctx.send(embed=embed)

    @commands.command()
    async def list(self, ctx: commands.Context):
        await ctx.send('Here is a list of commands for Hayato:\n`cvt` Convert units. Celsius/Fahrenheit and kg/lbs '
                       'converter is available.\n`dashsep` Separate every letter of your input with a '
                       'dash.\n`fascinated` Sends a certain number KouFascinated emote.\n`pick` Hayato will help you '
                       'pick one choice randomly.\n`verifyemail` Check if the email is plausible.\n`vowels` Count the '
                       'number of vowels in the input.')

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(random.choice(self.pings))


def setup(bot: commands.Bot):
    bot.add_cog(InfoCog(bot))
