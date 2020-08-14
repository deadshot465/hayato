import typing
import random
from discord.ext import commands


LOTTERY_DICT = {}


def add_player(name: str, numbers: str):
    # Separate the choices into a list
    number_list = numbers.split(',')
    # For each number remove the spaces
    number_set = set()
    for number in number_list:
        number = number.strip(' ')
        for char in number:
            if not char.isdigit():
                return 'There are invalid characters in the input!'
        if 1 <= int(number) <= 49:
            number_set.add(int(number))
        else:
            return 'You need numbers between 1 and 49!'
    if not len(number_set) == 6:
        return 'You need exactly 6 numbers!'
    LOTTERY_DICT[name] = number_set
    return 'Your request is successfully processed!'


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(description='Sends a certain number KouFascinated emote.', help='Send a single KouFascinated emote, or arbitrary number of KouFascinated emotes if specified. Max allowed emotes in a single message is subject to Discord\'s limitation.', aliases=['koufascinated'])
    async def fascinated(self, ctx: commands.Context, count: typing.Optional[int] = 0):
        result = ''
        if str(count) == '' or count == 0:
            result = 'https://cdn.discordapp.com/emojis/705279783340212265.gif'
        else:
            for i in range(0, count):
                result += '<a:KouFascinated:705279783340212265> '
        await ctx.send(result)

    @commands.command(description='Wanna try your luck?',
                      help='Join the lottery every week! Maybe you can gain a lot from it!')
    async def lottery(self,ctx: commands.Context, name: typing.Optional[str] = '', *, numbers: typing.Optional[str] = ''):
        if name == '':
            await ctx.send("Are you trying to fool me? Give me your name first!")
            return
        if numbers == '':
            await ctx.send("Are you trying to fool me? Give me the numbers!")
            return
        result = add_player(name, numbers)
        await ctx.send(result)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
