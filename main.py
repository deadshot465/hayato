import discord
import typing
import random
from datetime import datetime
from discord.ext import commands


DESCRIPTION = 'A Discord bot that can do some fun stuffs.'
bot = commands.Bot(command_prefix='h!', description=DESCRIPTION)
TRAINS = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7']
last_updated = datetime.now()
PINGS = ['pong', 'pang', 'pung']
DOMAINS = {'com', 'net', 'hk', 'org', 'ca', 'info'}

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


def cvt_lb_kg(lbs: float) -> float:
    return lbs / 2.2


def cvt_kg_lb(kg: float) -> float:
    return kg * 2.2


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
    game = discord.Game(random.choice(TRAINS))
    await bot.change_presence(status=discord.Status.online, activity=game)


def check_name_or_host(input_string: str) -> bool:
    '''
    (str) -> bool

    Return True if the name or host obeys the following rules:
    - NAME, HOST cannot contain any of {(, ), @, space}
    - NAME, HOST must be in between 1 and 100 characters
    >>> utoronto
    True
    >>> marco.miu
    True
    >>> de@gh(fe)
    False
    '''
    # Check if the name of host contains '(' or ')' or '@' or ' '
    # If there is, we have found an error
    error = False
    if '(' in input_string or ')' in input_string or '@' in input_string or ' ' in input_string:
        error = True
    else:
        # Else, check the length of the name and host
        # If the length is out the allowed range, we have found an error
        if len(input_string) < 1 or len(input_string) > 100:
            error = True
    return not error


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
    await ctx.send(random.choice(PINGS))


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
    elif unit1 == 'lbs' and unit2 == 'kg':
        answer = cvt_lb_kg(number)
        await ctx.send(str(number) + 'lbs is equal to ' + str(answer) + 'kg!')
    elif unit1 == 'kg' and unit2 == 'lbs':
        answer = cvt_kg_lb(number)
        await ctx.send(str(number) + 'kg is equal to ' + str(answer) + 'lbs!')
    else:
        await ctx.send('The inputted parameters are incorrect!')


@bot.command()
async def pick(ctx: discord.ext.commands.Context, all_choices: str):
    '''
    Input several choices that split with "," and Hayato will help you choose one.
    '''
    error = False
    # Separate the choices into a list
    choices = all_choices.split(',')
    # For each choice remove the spaces
    for index in range(0, len(choices)):
        choice = choices[index].strip(' ')
        # If someone tries to fool Hayato, it is impossible
        if choice == '':
            error = True
            break
        # Replace the choice with the no-blank-space one
        choices[index] = choice
    # Pick a random choice from the list
    hayato_choice = random.choice(choices)
    # Return the choice
    if error:
        await ctx.send('Are you trying to fool me?')
    else:
        await ctx.send('I pick **' + hayato_choice + '** for you!')


@bot.command()
async def fascinated(ctx: discord.ext.commands.Context, count: typing.Optional[int] = 0):
    result = ''
    if str(count) == '' or count == 0:
        result = 'https://cdn.discordapp.com/emojis/705279783340212265.gif'
    else:
        for i in range(0, count):
            result += '<a:KouFascinated:705279783340212265> '
    await ctx.send(result)


@bot.command()
async def verifyemail(ctx: discord.ext.commands.Context, email: str):
    '''
    (str) -> bool

    Return True if and only if the email is valid according to the following rules:
    - Must be formatted as NAME@HOST.DOMAIN
    - NAME, HOST cannot contain any of {(, ), @, space}
    - NAME, HOST must be in between 1 and 100 characters
    - DOMAIN must be in the set listed
    >>> verify_email('abc@def.com')
    True
    >>> verify_email('ab@c@de.f@.gh')
    False
    '''
    # Start of assuming no errors
    found_error = False
    # First check whether we can split the name, host and domain
    # If we cannot find @ and dot, there is an error
    name: str = ''
    host: str = ''
    domain: str = ''
    if not '@' in email or not '.' in email:
        found_error = True
    # else find the index of @ and .
    else:
        at_index = email.index('@')
        dot_index = email.rindex('.')
        # if index of @ > index of ., there is an error
        if at_index > dot_index:
            found_error = True
        # else we can split
        else:
            name = email[0:at_index]
            host = email[at_index + 1:dot_index]
            domain = email[dot_index + 1:]
    # Check name and host
    valid_name = check_name_or_host(name)
    valid_host = check_name_or_host(host)
    if valid_name == False or valid_host == False:
        found_error = True
    # Check domain
    if not domain in DOMAINS:
        found_error = True

    if found_error:
        await ctx.send('This email is not plausible!')
    else:
        await ctx.send('This email is plausible!')


@bot.command()
async def list(ctx: discord.ext.commands.Context):
    await ctx.send('Here is a list of commands for Hayato:\n`cvt` Convert units. Celsius/Fahrenheit and kg/lbs converter is available.\n`dashsep` Separate every letter of your input with a dash.\n`fascinated` Sends a certain number KouFascinated emote.\n`pick` Hayato will help you pick one choice randomly.\n`verifyemail` Check if the email is plausible.\n`vowels` Count the number of vowels in the input.')


@bot.command()
async def about(ctx: discord.ext.commands.Context):
    avatar_url = str(bot.user.avatar_url)
    embed = discord.Embed(color=discord.Color.from_rgb(30, 99, 175), description='Hayato is inspired by the anime Shinkalion. It is meant for practing making a Discord bot in Discord.py, but new features will be added from time to time.\n\nHayato version 1.0 was made and developed by:\n**Kirito#9286** and **Tetsuki Syu#1250**\nHayato Bot is licensed under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html').set_footer(text='Hayato Bot: Release 1.0 | 2020-07-28').set_author(name='Hayasugi Hayato from Shinkalion', icon_url=avatar_url).set_thumbnail(url='https://pbs.twimg.com/profile_images/1245939758695510016/UOG9MGdU_400x400.png')
    await ctx.send(embed=embed)



bot.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
