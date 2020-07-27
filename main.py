import discord
import random
from datetime import datetime
from discord.ext import commands


description = 'A Discord bot that can do some fun stuffs.'
bot = commands.Bot(command_prefix='h!', description=description)
trains = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7']
last_updated = datetime.now()
pings = ['pong', 'pang', 'pung']


# Count vowels
def count_vowels(string: str):
    count = 0
    for letter in string:
        if letter in 'AEIOUaeiou':
            count += 1
    return count


def cvt_c_f(celsius: float) -> float:
    '''(float) -> float
    Return the temperature in Fahrenheit.
    '''
    fahrenheit = celsius * 9 / 5 + 32
    return fahrenheit


def cvt_f_c(fahrenheit: float) -> float:
    '''(float) -> float
    Return the temperature in celsius.
    '''
    celsius = (fahrenheit - 32) * 5 / 9
    return celsius


# Dash separator
def dash_separator(string):
    '''(str) -> str
    Returns a string the separates each letter of the input string with a dash.

    >>> dash_separator('hello')
    h-e-l-l-o
    >>> Kirito
    K-i-r-i-t-o
    '''
    result = ''
    i = 0
    while i < len(string) - 1:
        result = result + string[i] + '-'
        i += 1
    result += string[i]
    return result


# Switch presence every hour
async def set_presence():
    game = discord.Game(random.choice(trains))
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    else:
        await bot.process_commands(message)
    global last_updated
    if (datetime.now() - last_updated).seconds > 3600:
        await set_presence()
        last_updated = datetime.now()


@bot.event
async def on_ready():
    print('Logged on as', bot.user)
    await set_presence()


@bot.command()
async def ping(ctx: discord.ext.commands.Context):
    await ctx.send(random.choice(pings))


@bot.command()
async def vowels(ctx: discord.ext.commands.Context, string: str):
    if len(string) <= 0:
        await ctx.send('No message found...')
    answer = count_vowels(string)
    await ctx.send('There are ' + str(answer) + ' vowels in the input!')


@bot.command()
async def dashsep(ctx: discord.ext.commands.Context, string: str):
    if len(string) <= 0:
        await ctx.send('No message found...')
    answer = dash_separator(string)
    await ctx.send(answer)


@bot.command()
async def cvt(ctx: discord.ext.commands.Context, unit1: str, unit2: str, number: float):
    if unit1 == 'f' and unit2 == 'c':
        answer = cvt_f_c(number)
        await ctx.send(str(number) + '\u2109' + ' is equal to ' + str(answer) + '\u2103.')
    elif unit1 == 'c' and unit2 == 'f':
        answer = cvt_c_f(number)
        await ctx.send(str(number) + '\u2103' + ' is equal to ' + str(answer) + '\u2109.')
    else:
        await ctx.send('The inputted parameters are incorrect!')


bot.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
