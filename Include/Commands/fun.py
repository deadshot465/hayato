import asyncio
import datetime
import discord
import json
import marshmallow_dataclass
import typing
import random
from discord.ext import commands
from Include.Commands.lottery.lottery import LotteryParticipant
from Include.Utils.utils import USER_MENTION_REGEX
from marshmallow import Schema
from Utils.credit_manager import CreditManager


LOTTERY_RUNNING = False
EIGHTBALL_RESPONSE = ['Of course', 'It is certain', 'I think so', 'Maybe', 'If you like Shinkansen, then yes',
                      'I think this is as reliable as Shinkansen trains', 'This is as good as E5 Series',
                      'Uhh...I am not sure', 'I don\'t want to tell you now, because I am watching Shinkalion now',
                      'This question is like asking me if Shinkansen is rapid or not',
                      'I am tired now, ask me later', 'Sorry, I don\'t know', 'Think about it again and ask me later',
                      'Definitely no', 'Of course no, don\'t ask me the same question again', 'I guess no', 'Maybe not']


def switch_on():
    global LOTTERY_RUNNING
    LOTTERY_RUNNING = True


# Also we use an user instead of an arbitrary name.
async def add_player(ctx: commands.Context, numbers: str, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    author: typing.Union[discord.User, discord.Member] = ctx.author
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
        if (await CreditManager.get_user_credits(ctx, participant.user_id)) - 10 < 0:
            return 'You don\'t have enough credits to buy the lottery!'
        await CreditManager.remove_credits(participant.user_id, 10)
        if participant.username != author.display_name:
            participant.username = author.display_name
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return '{}, you have successfully bought a lottery of `{}`! Deducted 10 credits from your account.'.format(author.display_name, str(sorted(number_set)))
    else:
        participant = LotteryParticipant(author.display_name, author.id, list(), datetime.datetime.now(), datetime.datetime.now())
        participant.lottery_choices.append(sorted(number_set))
        lottery_data.append(participant)
        await CreditManager.add_credits(author.id, 100, insert=True)
        serialized = schema().dumps(lottery_data, many=True)
        with open('Storage/lottery.json', 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return '{}, you have got your 100 starting credits! You have successfully bought a lottery of `{}`!'.format(author.display_name, str(sorted(number_set)))


async def get_daily(ctx: commands.Context, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    author: typing.Union[discord.User, discord.Member] = ctx.author
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        elapsed_time = datetime.datetime.now() - participant.last_daily_time
        if elapsed_time.total_seconds() > 86400:
            await CreditManager.add_credits(participant.user_id, 10, ctx=ctx)
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


async def get_weekly(ctx: commands.Context, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    author: typing.Union[discord.User, discord.Member] = ctx.author
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        elapsed_time = datetime.datetime.now() - participant.last_weekly_time
        if elapsed_time.total_seconds() > 604800:
            await CreditManager.add_credits(participant.user_id, 30, ctx=ctx)
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


async def get_balance(ctx: commands.Context, lottery_data: typing.List[LotteryParticipant]):
    author: typing.Union[discord.User, discord.Member] = ctx.author
    participant_data = list(filter(lambda x: x.user_id == author.id, lottery_data))
    participant: LotteryParticipant
    if len(participant_data) > 0:
        participant = participant_data[0]
        embed = discord.Embed(title='Account Balance', description='Here is your account balance:', colour=discord.Colour.from_rgb(30, 99, 175))
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.add_field(name='Credits', value=str(await CreditManager.get_user_credits(ctx, participant.user_id, True)), inline=True)
        return embed
    else:
        return 'You need to create an account by buying a lottery first! The first lottery that you buy is free.'


async def compare_numbers(ctx: commands.Context, drawn_numbers: list, lottery_data: typing.List[LotteryParticipant], schema: typing.Type[Schema]):
    result_text: typing.List[typing.List[str]] = list()
    result_text.append(list())
    current_index = 0
    embed = discord.Embed(title='Lottery Result', description='',
                          color=discord.Colour.from_rgb(30, 99, 175))
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/734604988717858846/744736053264515133/IMGBIN_lottery-machine-illustration-png_nU9g7tRi.png')
    for participant in lottery_data:
        player_numbers_list = participant.lottery_choices
        total_credits = 0
        for numbers_set in enumerate(player_numbers_list):
            count = 0
            for number in numbers_set[1]:
                if number in drawn_numbers:
                    count += 1
            if count == 2:
                add_credits = 10
            elif count == 3:
                add_credits = 50
            elif count == 4:
                add_credits = 500
            elif count == 5:
                add_credits = 1000
            elif count == 6:
                add_credits = 3000
            else:
                add_credits = 0
            total_credits += add_credits
            if len('\n'.join(result_text[current_index])) >= 2000:
                result_text.append(list())
                current_index += 1
            result_text[current_index].append('{}\'s lottery #{} hits **{}** numbers! You gained **{}** credits!'.format(participant.username, numbers_set[0] + 1, count, add_credits))
        await CreditManager.add_credits(participant.user_id, total_credits)
        embed.add_field(name=participant.username, value=str(total_credits), inline=True)
        participant.lottery_choices.clear()
    for text in result_text:
        embed.description = '\n'.join(text)
        await ctx.send(embed=embed)
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
    async def lottery(self, ctx: commands.Context, *, args: typing.Optional[str] = ''):
        if args.lower().startswith('transfer') or args.lower().startswith('trade'):
            # Split all texts following the command.
            args = list(map(lambda x: x.strip(), args.split(' ')))
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
            if (await CreditManager.get_user_credits(ctx, participants_1[0].user_id)) - amount < 0:
                await ctx.send('You cannot transfer more credits than you currently have!')
                return
            if len(participants_2) == 0:
                await ctx.send('Sorry! I cannot find the user you want to transfer credits to.\nEither the user does not exist, or the user has\'t joined in the lottery yet.')
                return
            await CreditManager.remove_credits(participants_1[0].user_id, amount)
            await CreditManager.add_credits(participants_2[0].user_id, amount)
            serialized = Fun.participant_schema().dumps(Fun.lottery_data, many=True)
            with open('Storage/lottery.json', 'w') as file_1:
                obj = json.loads(serialized)
                file_1.write(json.dumps(obj, indent=2))
            embed = discord.Embed(title='Transfer Credits', description='{} has transferred {} credits to {}!'.format(participants_1[0].username, amount, participants_2[0].username), color=self.color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name='Balance', value=str(await CreditManager.get_user_credits(ctx, participants_1[0].user_id)), inline=False)
            await ctx.send(embed=embed)

        elif args == 'info':
            desc = 'Welcome to the lottery hosted by Hayato!\n\n' \
                   'To join the lottery, you need to set up an account first. You can buy your first lottery for free and set up an account. The command will be `h!lottery <numbers>` (numbers must be separated by a comma). You need to choose exactly 6 distinct numbers between 1 and 49 in order to buy a lottery ticket. Or, if you don\'t know what numbers to choose, you can use `h!lottery` to let me choose for you! After that, you will receive 100 starting credits. You can buy more than one lottery tickets, and each ticket will cost you 10 credits.\n\n' \
                   'Moderators will start the lottery regularly. 6 numbers will be drawn from each lottery. The reward system is as follows:\n' \
                   '0/1 numbers match: 0 credits\n' \
                   '2 numbers match: 10 credits\n' \
                   '3 numbers match: 50 credits\n' \
                   '4 numbers match: 500 credits\n' \
                   '5 numbers match: 1000 credits\n' \
                   '6 numbers match: 3000 credits\n\n' \
                   'You can get daily and weekly credits with the command `h!lottery daily` and `h!lottery weekly`. Within a 24-hour period, you can receive 10 credits. You can also receive 30 credits for every 7 days. If you don’t have enough credits, or you want to give some credits to your friends, you can transfer credits with them. The command is `h!lottery transfer <amount> <recipient>`. You must ping the recipient in order to finish the transaction.\n\n' \
                   'To see the lotteries you have bought so far, type `h!lottery list`.\n\n' \
                   'Good luck!\n\n' \
                   'Examples of commands:\n`h!lottery 1,2,3,4,5,6` Correct\n`h!lottery 1-2-3-4-5-6` Incorrect, numbers must be separated by comma\n`h!lottery 2,2,3,5,7,7` Incorrect, numbers cannot be repeated.'
            embed = discord.Embed(title='Lottery', description=desc, colour=self.color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/734604988717858846/744736053264515133/IMGBIN_lottery-machine-illustration-png_nU9g7tRi.png')
            await ctx.send(embed=embed)
        elif args == 'start':
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
        elif args == 'daily':
            result = await get_daily(ctx, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)
        elif args == 'weekly':
            result = await get_weekly(ctx, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)
        elif args == 'balance' or args == 'account':
            result = await get_balance(ctx, Fun.lottery_data)
            if isinstance(result, str):
                await ctx.send(result)
            else:
                await ctx.send(embed=result)
        elif args == 'list':
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
        elif args == 'help':
            desc = 'Here is a list of commands available for the lottery.\n\n Create an account / buy a lottery with random numbers: `h!lottery`\n' \
                   'Buy a lottery with desired numbers: `h!lottery <numbers>` (6 distinct numbers, separated by commas)\n' \
                   'Get daily/weekly credits: `h!lottery daily` / `h!lottery weekly`\n' \
                   'Check balance: `h!lottery balance`\n' \
                   'Check bought lotteries: `h!lottery list`\n' \
                   'Transfer credits to another person: `h!lottery transfer <amount> <recipient>`'
            embed = discord.Embed(title='Lottery Commands', description=desc, color=self.color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        elif args == '':
            random_numbers: typing.Set[str] = set()
            while len(random_numbers) < 6:
                random_numbers.add(str(random.randint(1, 49)))
            args = ','.join(random_numbers)
            result = await add_player(ctx, args, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)
        else:
            result = await add_player(ctx, args, Fun.lottery_data, self.participant_schema)
            await ctx.send(result)

    @commands.command(description='Get an answer from a yes/no question.',
                      help='You can ask a yes/no question to Hayato, and Hayato will give you an answer.', name='8ball')
    async def eightball(self, ctx: commands.Context, *, args: typing.Optional[str]):
        if args is None:
            await ctx.send('🎱 | Please give me a question first, **' + ctx.author.display_name + '**!')
            return
        await ctx.send('🎱 | {}, **{}**!'.format(random.choice(EIGHTBALL_RESPONSE), ctx.author.display_name))

    @commands.command(description='Play a coinflip game with Hayato.',
                      help='Guess whether the coinflip result is head or tail, and earn credits from it.', aliases=['cf'])
    async def coinflip(self, ctx: commands.Context, arg1: typing.Optional[str], arg2: typing.Optional[str]):
        author: typing.Union[discord.User, discord.Member] = ctx.author
        await CreditManager.get_user_credits(ctx, author.id, True)
        coin = ['h', 't']
        words = {'h': 'head', 't': 'tail'}
        if arg1 is None or arg1.lower() not in coin:
            await ctx.send('You need to guess if it is head or tail. The correct input is `h!coinflip <h/t> <amount>`!')
            return
        if arg2 is None:
            await ctx.send('You need to specify the amount for this round. The correct input is `h!coinflip <h/t> <amount>`!')
            return
        try:
            amount = int(arg2)
            if amount < 1:
                await ctx.send('You cannot input non-positive values of credits!')
                return
            answer = random.choice(coin)
            if arg1.lower() == answer:
                await CreditManager.add_credits(author.id, amount, ctx=ctx)
                await ctx.send('It is **{}**! You gained {} credits!'.format(words.get(answer), amount))
            else:
                await CreditManager.remove_credits(author.id, amount, ctx=ctx)
                await ctx.send('It is **{}**! You lost {} credits!'.format(words.get(answer), amount))
        except ValueError as e:
            await ctx.send('The amount that you input is invalid!')
        return


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
