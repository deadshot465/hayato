import discord
import typing
import random
import time
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
    if LOTTERY_DICT.get(name) is None:
        LOTTERY_DICT[name] = []
    LOTTERY_DICT[name].append(number_set)
    return 'Your request is successfully processed!'


def compare_numbers(drawn_numbers: list):
    result_dict = {}
    for name in LOTTERY_DICT:
        player_numbers_list = LOTTERY_DICT[name]
        for numbers_set in player_numbers_list:
            count = 0
            for number in numbers_set:
                if number in drawn_numbers:
                    count += 1
            if result_dict.get(name) is None:
                result_dict[name] = []
            result_dict[name].append(count)
    LOTTERY_DICT.clear()
    return result_dict


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
    async def lottery(self,ctx: commands.Context, *, numbers: typing.Optional[str] = ''):
        if numbers == 'start':
            permission: discord.Permissions = ctx.author.permissions_in(ctx.channel)
            is_administrator = permission.administrator
            if not is_administrator:
                await ctx.send('You are not an administrator, you can\'t start the lottery yourself!')
                return
            else:
                await ctx.send('The lottery will start in 10 seconds!')
                time.sleep(1)
                drawn_numbers = []
                word_list = ['first', 'second', 'third', 'fourth', 'fifth', 'last']
                for word in word_list:
                    number = random.randint(1, 49)
                    while number in drawn_numbers:
                        number = random.randint(1, 49)
                    drawn_numbers.append(number)
                    await ctx.send('The ' + word + ' drawn number is **' + str(number) + '**!')
                    time.sleep(1)
                drawn_numbers.sort()
                await ctx.send('The drawn numbers are: ' + ''.join(str(drawn_numbers)))
                result = compare_numbers(drawn_numbers)
                for player in result:
                    await ctx.send(player.display_name + ' hits **' + str(result[player]) + '** numbers!')
                return
        if numbers == '':
            await ctx.send("Are you trying to fool me? Give me the numbers!")
            return
        else:
            name = ctx.author
            result = add_player(name, numbers)
        await ctx.send(result)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
