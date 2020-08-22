import discord
import help
import os
import random
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv(verbose=True)
# A simple description of our bot.
DESCRIPTION = 'A Discord bot that can do some fun stuffs.'
# Various trains for Hayato to play.
TRAINS = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7']
RESPONSE = ['I am a punctual and trustworthy man!', 'Hello! My name is Hayasugi Hayato. Nice to meet you!', 'Uhh...I am afraid of heights...Don\'t tell me to board an airplane!', 'Change form, Shinkalion!', 'My dream is to be a Shinkansen train conductor!', 'All people who like Shinkansen are good people!', 'Shinkansen trains are so cool!', 'Shinkansen E5 Series is my favourite!', 'Do you know how much it costs for a Shinkansen trip from Tokyo to Osaka?']

# Available cogs. Path is separated with dots, without file extensions.
EXTENSIONS = ['Include.Commands.fun',
              'Include.Commands.info',
              'Include.Commands.rails',
              'Include.Commands.utility']

# Initialize our bot and set the prefix to 'h!', also set up the description and help command.
HELP = {
    'description': 'List and show helps for available commands.',
    'help': 'List available commands. Specifying a category will show available commands under that specific category. Specifying a command will show detailed usage and description of that command.',
    'aliases': ['manual']
}

# Load prefix from .env file, or use a default prefix.
PREFIX = os.getenv('PREFIX') or 'h!'
bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, help_command=help.Help(command_attrs=HELP))
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
        lower_case = message.content.lower()
        if '<@737017231522922556>' in lower_case or 'hayato' in lower_case:
            chance = random.randint(1, 100)
            if chance > 70:
                channel = message.channel
                await channel.send(random.choice(RESPONSE))
        else:
            chance = random.randint(1, 100)
            if chance > 95:
                channel = message.channel
                await channel.send(random.choice(RESPONSE))
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

bot.run(os.getenv('TOKEN'), bot=True, reconnect=True)


def test_bot():
    return
