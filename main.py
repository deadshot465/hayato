import discord
import random
from datetime import datetime
from discord.ext import commands

# A simple description of our bot.
DESCRIPTION = 'A Discord bot that can do some fun stuffs.'
# Various trains for Hayato to play.
TRAINS = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7']
# Available domains.
DOMAINS = {'com', 'net', 'hk', 'org', 'ca', 'info'}
# Available cogs. Path is separated with dots, without file extensions.
EXTENSIONS = ['Include.Commands.fun',
              'Include.Commands.info',
              'Include.Commands.utility']

# Initialize our bot and set the prefix to 'h!', also set up the description.
bot = commands.Bot(command_prefix='h!', description=DESCRIPTION)
# Record the initial update time for switching presences every hour.
last_updated = datetime.now()


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


if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)
    print('Extensions successfully loaded.')

bot.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM', bot=True, reconnect=True)

