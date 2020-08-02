import discord
import help
import random
from datetime import datetime
from discord.ext import commands

# A simple description of our bot.
DESCRIPTION = 'A Discord bot that can do some fun stuffs.'
# Various trains for Hayato to play.
TRAINS = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7']

# Available cogs. Path is separated with dots, without file extensions.
EXTENSIONS = ['Include.Commands.fun',
              'Include.Commands.info',
              'Include.Commands.japan_railway',
              'Include.Commands.utility']

# Initialize our bot and set the prefix to 'h!', also set up the description and help command.
HELP = {
    'description': 'List and show helps for available commands.',
    'help': 'List available commands. Specifying a category will show available commands under that specific category. Specifying a command will show detailed usage and description of that command.',
    'aliases': ['manual']
}
bot = commands.Bot(command_prefix='h!', description=DESCRIPTION, help_command=help.Help(command_attrs=HELP))
# Record the initial update time for switching presences every hour.
last_updated = datetime.now()


# Switch presence every hour
async def set_presence():
    game = discord.Game(random.choice(TRAINS))
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


if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)
    print('Extensions successfully loaded.')

bot.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM', bot=True, reconnect=True)


def test_bot():
    return
