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
from Include.Utils.utils import USER_MENTION_REGEX
from marshmallow import Schema


LOTTERY_RUNNING = False
EIGHTBALL_RESPONSE = ['Of course', 'It is certain', 'I think so', 'Maybe', 'If you like Shinkansen, then yes',
                      'Uhh...I am not sure', 'I don\'t want to tell you now, because I am watching Shinkalion now',
                      'This question is like asking me if Shinkansen is rapid or not',
                      'I am tired now, ask me later', 'Sorry, I don\'t know', 'Definitely no',
                      'Of course no, don\'t ask me the same question again', 'I guess no']

def switch_on():
    global LOTTERY_RUNNING
    LOTTERY_RUNNING = True


# Also we use an user instead of an arbitrary name.
def add_player(author: typing.Union[discord.User, discord.Member], numbers: str, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    if LOTTERY_RUNNING:
        return 'There is a lottery running now! Please try again after the lottery is over!'
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
        if participant.credits - 10 < 0:
            return 'You don\'t have enough credits to buy the lottery!'
        participant.credits = participant.credits - 10
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return 'You have successfully bought a lottery of `{}`! Deducted 10 credits from your account.'.format(str(sorted(number_set)))
    else:
        participant = LotteryParticipant(author.display_name, author.id, list(), 100, datetime.datetime.now(), datetime.datetime.now())
        participant.lottery_choices.append(sorted(number_set))
        lottery_data.append(participant)
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return 'You have got your 100 starting credits! You have successfully bought a lottery of `{}`!'.format(str(sorted(number_set)))


def get_daily(author: typing.Union[discord.User, discord.Member], lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        elapsed_time = datetime.datetime.now() - participant.last_daily_time
        if elapsed_time.total_seconds() > 86400:
            participant.credits += 10
            participant.last_daily_time = datetime.datetime.now()
            serialized = schema().dumps(lottery_data, many=True)
            with open('Storage/lottery.json', 'w') as file_1:
                obj = json.loads(serialized)
                file_1.write(json.dumps(obj, indent=2))
            return 'You have received your daily 10 credits!'
        else:
            seconds_left = 86400 - elapsed_time.seconds
            hours = seconds_left // 60 // 60
            leftover_sec = seconds_left - (hours * 60 * 60)
            minutes = leftover_sec // 60
            seconds = leftover_sec - (60 * minutes)
            result = '%02d:%02d:%02d' % (hours, minutes, seconds)
            return 'You need to wait at least 24 hours to receive the next daily credits! Time left: ' + result
    else:
        return 'You need to create an account by buying a lottery first! The first lottery that you buy is free.'


def get_weekly(author: typing.Union[discord.User, discord.Member], lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        elapsed_time = datetime.datetime.now() - participant.last_weekly_time
        if elapsed_time.total_seconds() > 604800:
            participant.credits += 30
            participant.last_weekly_time = datetime.datetime.now()
            serialized = schema().dumps(lottery_data, many=True)
            with open('Storage/lottery.json', 'w') as file_1:
                obj = json.loads(serialized)
                file_1.write(json.dumps(obj, indent=2))
            return 'You have received your weekly 30 credits!'
        else:
            days = 7 - elapsed_time.total_seconds() / 60 / 60 / 24
            hours = (days - int(days)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            result = '%01d Days %02d:%02d:%02d' % (days, hours, minutes, seconds)
            return 'You need to wait at least 7 days to receive the next weekly credits! Time left: ' + result
    else:
        return 'You need to create an account by buying a lottery first! The first lottery that you buy is free.'


def get_balance(author: typing.Union[discord.User, discord.Member], lottery_data: typing.List[LotteryParticipant]):
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        embed = discord.Embed(description='Here is your account balance:', colour=discord.Colour.from_rgb(30, 99, 175))
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.add_field(name='Credits', value=str(participant.credits), inline=True)
        return embed
    else:
        return 'You need to create an account by buying a lottery first! The first lottery that you buy is free.'


async def compare_numbers(ctx: commands.Context, drawn_numbers: list, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    for participant in lottery_data:
        player_numbers_list = participant.lottery_choices
        for numbers_set in enumerate(player_numbers_list):
            count = 0
            for number in numbers_set[1]:
                if number in drawn_numbers:
                    count += 1
            if count == 2:
                add_credits = 10
                participant.credits += add_credits
            elif count == 3:
                add_credits = 50
                participant.credits += add_credits
            elif count == 4:
                add_credits = 150
                participant.credits += add_credits
            elif count == 5:
                add_credits = 500
                participant.credits += add_credits
            elif count == 6:
                add_credits = 2000
                participant.credits += add_credits
            else:
                add_credits = 0
            await ctx.send('{}\'s lottery #{} hits **{}** numbers! You gained **{}** credits!'.format(participant.username, numbers_set[0] + 1, count, add_credits))
            count = 0
        participant.lottery_choices.clear()
        global LOTTERY_RUNNING
        LOTTERY_RUNNING = False
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
        self.color = discord.Colour.from_rgb(30, 99, 175)

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
        if numbers.lower().startswith('transfer') or numbers.lower().startswith('trade'):
            # Split all texts following the command.
            args = list(map(lambda x: x.strip(), numbers.split(' ')))
            # Pop out the first argument, which in this case might be 'transfer' or 'trade.'
            args.pop(0)
            # Get the amount to trade.
            try:
                amount = int(args.pop(0))
            except ValueError:
                await ctx.send('Please input a correct amount of credits to transfer!')
                return
            if USER_MENTION_REGEX.match(args[0]) is None:
                await ctx.send('The second argument has to be a valid user mention!')
                return
            elif amount < 0:
                await ctx.send('You can\'t trade with negative amounts!')
                return
            participants_1 = list(filter(lambda x: x.user_id == ctx.author.id, self.lottery_data))
            target_id = USER_MENTION_REGEX.match(args[0]).group(1)
            participants_2 = list(filter(lambda x: x.user_id == int(target_id), self.lottery_data))
            if len(participants_1) == 0:
                await ctx.send('You can\'t trade with other people when you don\'t have an account!\nCreate an account first by buying a lottery.')
                return
            if participants_1[0].credits - amount < 0:
                await ctx.send('You cannot transfer more credits than you currently have!')
                return
            if len(participants_2) == 0:
                await ctx.send('Sorry! I cannot find the user you want to transfer credits to.\nEither the user does not exist, or the user has\'t joined in the lottery yet.')
                return
            participants_1[0].credits -= amount
            participants_2[0].credits += amount
            serialized = Fun.participant_schema().dumps(Fun.lottery_data, many=True)
            with open('Storage/lottery.json', 'w') as file_1:
                obj = json.loads(serialized)
                file_1.write(json.dumps(obj, indent=2))
            embed = discord.Embed(title='Transfer Credits', description='{} has transferred {} credits to {}!'.format(participants_1[0].username, amount, participants_2[0].username), color=self.color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name='Balance', value=str(participants_1[0].credits), inline=False)
            await ctx.send(embed=embed)

        elif numbers == 'info':
            desc = 'Welcome to the lottery hosted by Hayato!\n\n' \
                   'To join the lottery, you need to set up an account first. You can buy your first lottery for free and set up an account. The command will be `h!lottery <numbers>` (numbers must be separated by a comma). You need to choose exactly 6 distinct numbers between 1 and 49 in order to buy a lottery ticket. Or, if you don\'t know what numbers to choose, you can use `h!lottery` to let me choose for you! After that, you will receive 100 starting credits. You can buy more than one lottery tickets, and each ticket will cost you 10 credits.\n\n' \
                   'Moderators will start the lottery regularly. 6 numbers will be drawn from each lottery. The reward system is as follows:\n' \
                   '0/1 numbers match: 0 credits\n' \
                   '2 numbers match: 10 credits\n' \
                   '3 numbers match: 50 credits\n' \
                   '4 numbers match: 150 credits\n' \
                   '5 numbers match: 500 credits\n' \
                   '6 numbers match: 2000 credits\n\n' \
                   'You can get daily and weekly credits with the command `h!lottery daily` and `h!lottery weekly`. Within a 24-hour period, you can receive 10 credits. You can also receive 30 credits for every 7 days. If you don’t have enough credits, or you want to give some credits to your friends, you can transfer credits with them. The command is `h!lottery transfer <amount> <recipient>`. You must ping the recipient in order to finish the transaction.\n\n' \
                   'To see the lotteries you have bought so far, type `h!lottery list`.\n\n' \
                   'Good luck!\n\n' \
                   'Examples of commands:\n`h!lottery 1,2,3,4,5,6` Correct\n`h!lottery 1-2-3-4-5-6` Incorrect, numbers must be separated by comma\n`h!lottery 2,2,3,5,7,7` Incorrect, numbers cannot be repeated.'
            embed = discord.Embed(title='Lottery', description=desc, colour=self.color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/734604988717858846/744736053264515133/IMGBIN_lottery-machine-illustration-png_nU9g7tRi.png')
            await ctx.send(embed=embed)
        elif numbers == 'start':
            permission: discord.Permissions = ctx.author.permissions_in(ctx.channel)
            is_administrator = permission.administrator
            if not is_administrator:
                await ctx.send('You are not an administrator, you can\'t start the lottery yourself!')
            else:
                global LOTTERY_RUNNING
                if LOTTERY_RUNNING:
                    await ctx.send('There is already a lottery running now!')
                    return
                switch_on()
                await ctx.send('The lottery will start in 10 seconds!')
                await asyncio.sleep(10)
                drawn_numbers = []
                word_list = ['first', 'second', 'third', 'fourth', 'fifth', 'last']
                for word in word_list:
                    number = random.randint(1, 49)
                    while number in drawn_numbers:
                        number = random.randint(1, 49)
                    drawn_numbers.append(number)
                    await ctx.send('The ' + word + ' drawn number is **' + str(number) + '**!')
                    await asyncio.sleep(3)
                drawn_numbers.sort()
                await ctx.send('The drawn numbers are: ' + ''.join(str(drawn_numbers)))
                await compare_numbers(ctx, drawn_numbers, Fun.lottery_data, self.participant_schema)
        elif numbers == 'daily':
            result = get_daily(ctx.author, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)
        elif numbers == 'weekly':
            result = get_weekly(ctx.author, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)
        elif numbers == 'balance' or numbers == 'account':
            result = get_balance(ctx.author, Fun.lottery_data)
            if isinstance(result, str):
                await ctx.send(result)
            else:
                await ctx.send(embed=result)
        elif numbers == 'list':
            participant = list(filter(lambda a: a.user_id == ctx.author.id, Fun.lottery_data))
            if len(participant) == 0:
                await ctx.send('You are not in the lottery game yet!\nBuy a lottery to join in the game.')
                return
            participant_lotteries = participant[0].lottery_choices
            if len(participant_lotteries) == 0:
                await ctx.send('You currently don\'t have any lotteries!')
                return
            embed = discord.Embed(title='Purchased Lotteries', description='The following are your currently purchased lotteries.', color=self.color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            lotteries = list(map(lambda b: '[{}]'.format(', '.join(list(map(lambda c: str(c), b)))), participant_lotteries))
            embed.add_field(name='Lotteries', value='\n'.join(lotteries), inline=False)
            await ctx.send(embed=embed)
        elif numbers == '':
            random_numbers: typing.Set[str] = set()
            while len(random_numbers) < 6:
                random_numbers.add(str(random.randint(1, 49)))
            numbers = ','.join(random_numbers)
            result = add_player(ctx.author, numbers, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)
        else:
            result = add_player(ctx.author, numbers, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)

    @commands.command(description='Get an answer from a yes/no question.',
                      help='You can ask a yes/no question to Hayato, and Hayato will give you an answer.', name='8ball')
    async def eightball(self, ctx: commands.Context, *, args: str):
        await ctx.send('🎱 | {}, **{}**!'.format(random.choice(EIGHTBALL_RESPONSE), ctx.author.display_name))


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
