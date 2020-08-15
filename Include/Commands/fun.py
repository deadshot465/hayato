import asyncio
import datetime
import discord
import json
import marshmallow_dataclass
import typing
import random
import time
from discord.ext import commands
from Include.Commands.lottery.lottery import LotteryParticipant
from marshmallow import Schema


# We don't use a global dictionary anymore.
# LOTTERY_DICT = {}


# Also we use an user instead of an arbitrary name.
def add_player(author: typing.Union[discord.User, discord.Member], numbers: str, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
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
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        if participant.lottery_choices is None:
            participant.lottery_choices = list()
        participant.lottery_choices.append(sorted(number_set))
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return 'Your request is successfully processed!'
    else:
        participant = LotteryParticipant(author.display_name, author.id, list(), 0, datetime.datetime.now())
        participant.lottery_choices.append(sorted(number_set))
        lottery_data.append(participant)
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return 'Your request is successfully processed!'


async def compare_numbers(ctx: commands.Context, drawn_numbers: list, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    for participant in lottery_data:
        player_numbers_list = participant.lottery_choices
        for numbers_set in enumerate(player_numbers_list):
            count = 0
            for number in numbers_set[1]:
                if number in drawn_numbers:
                    count += 1
            await ctx.send('{}\'s lottery #{} hits **{}** numbers!'.format(participant.username, numbers_set[0] + 1, count))
            count = 0
        participant.lottery_choices.clear()
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))


class Fun(commands.Cog):
    participant_schema = marshmallow_dataclass.class_schema(LotteryParticipant)
    with open('Storage/lottery.json') as file_1:
        lottery_data: typing.List[LotteryParticipant] = participant_schema().loads(json_data=file_1.read(), many=True)

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
                await compare_numbers(ctx, drawn_numbers, Fun.lottery_data, self.participant_schema)
                return
        if numbers == '':
            await ctx.send("Are you trying to fool me? Give me the numbers!")
            return
        else:
            name = ctx.author
            result = add_player(ctx.author, numbers, Fun.lottery_data, self.participant_schema)
        await ctx.send(result)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
