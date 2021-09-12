import asyncio
import discord
import help
import os
import random
from datetime import datetime
from typing import List, Optional, Union

from discord.ext import commands
from dotenv import load_dotenv
from Include.Commands.fun import auto_lottery
from services.credit_service import CreditService
from utils.configuration_manager import ConfigurationManager

load_dotenv(verbose=True)
# A simple description of our bot.
DESCRIPTION = 'A Discord bot that can do some fun stuffs.'
# Various trains for Hayato to play.
TRAINS = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7', 'JR East E233', 'JR East E235']
RESPONSE = ['I am a punctual and trustworthy man!', 'Hello! My name is Hayasugi Hayato. Nice to meet you!', 'Uhh...I am afraid of heights...Don\'t tell me to board an airplane!', 'Change form, Shinkalion!', 'My dream is to be a Shinkansen train conductor!', 'All people who like Shinkansen are good people!', 'Shinkansen trains are so cool!', 'Shinkansen E5 Series is my favourite!', 'Do you know how much it costs for a Shinkansen trip from Tokyo to Osaka?']

# Available cogs. Path is separated with dots, without file extensions.
EXTENSIONS = ['Include.Commands.admin',
              'Include.Commands.fun',
              'Include.Commands.info',
              'Include.Commands.rails',
              'Include.Commands.utility']

ADMIN_COMMANDS = ['enable', 'disable', 'allow', 'ignore', 'warn', 'ban']

# Initialize our bot and set the prefix to 'h!', also set up the description and help command.
HELP = {
    'description': 'List and show helps for available commands.',
    'help': 'List available commands. Specifying a category will show available commands under that specific category. Specifying a command will show detailed usage and description of that command.',
    'aliases': ['manual']
}

# Setup intents.
intents = discord.Intents.default()
intents.members = True
intents.presences = True
# Load prefix from .env file, or use a default prefix.
PREFIX = os.getenv('PREFIX') or 'h!'
bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, help_command=help.Help(command_attrs=HELP), intents=intents)


# Change the initial presence and set up a loop that changes the presence every hour
async def set_presence():
    game = discord.Game(random.choice(TRAINS))
    await bot.change_presence(status=discord.Status.online, activity=game)
    asyncio.create_task(update_presence())


# The main function that updates the presence every hour
async def update_presence():
    try:
        await asyncio.sleep(3600)
        game = discord.Game(random.choice(TRAINS))
        await bot.change_presence(status=discord.Status.online, activity=game)
        asyncio.create_task(update_presence())
    except Exception as e:
        print(e)


@bot.event
async def on_message(message: discord.Message):
    if message.author.id == 565305035592957954 and len(message.embeds) > 0:
        try:
            embed = message.embeds[0]
            if 'won the game' in embed.title.lower():
                title: str = embed.title
                index = title.index(' ')
                username = title[0:index]
                guild: Optional[discord.Guild] = message.guild
                members: List[discord.Member] = guild.members
                match_members = list(filter(lambda x: x.display_name.startswith(username), members))
                if len(match_members) == 0:
                    match_members = list(filter(lambda x: x.name.startswith(username), members))
                await CreditService.add_credits(int(match_members[0].id), 20, channel_id=716483752544698450,
                                                channel=message.channel)
        except AttributeError:
            pass
        except IndexError:
            pass

    # Don't do anything to messages from Hayato himself.
    if message.author == bot.user:
        return

    # Strip out prefix so we can get the command name to test if it's used in a valid channel.
    command: str = message.content.strip(os.getenv('PREFIX')).lower()
    # Allow admin commands.
    for cmd in ADMIN_COMMANDS:
        if command.startswith(cmd):
            await bot.process_commands(message)
            return
    # Process commands in valid channels only.
    if message.channel.id in ConfigurationManager.get_available_channels():
        await bot.process_commands(message)

    # Don't reply to bot users including Hayato himself.
    if message.author.bot:
        return
    # Don't reply in ignored channels.
    if message.channel.id in ConfigurationManager.get_ignored_channels():
        return
    # Change message content to lowercase for comparison.
    lower_case = message.content.lower()
    if '<@737017231522922556>' in lower_case or 'hayato' in lower_case:
        chance = random.randint(1, 100)
        if chance > 85:
            channel = message.channel
            await channel.send(random.choice(RESPONSE))
    else:
        chance = random.randint(1, 100)
        if chance > 97:
            channel = message.channel
            await channel.send(random.choice(RESPONSE))


async def schedule_lottery():
    next_lottery_time = ConfigurationManager.get_next_lottery_time()
    seconds = (next_lottery_time - datetime.now()).total_seconds()
    try:
        await asyncio.sleep(seconds)
        channel: Optional[Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]] = bot.get_channel(744550089908813945)
        if isinstance(channel, discord.TextChannel):
            await auto_lottery(channel)
            ConfigurationManager.set_next_lottery_time()
            asyncio.create_task(schedule_lottery())
    except Exception as e:
        print(e)


@bot.event
async def on_ready():
    await CreditService.initialize()
    print('Logged on as', bot.user)
    await set_presence()
    asyncio.create_task(schedule_lottery())


if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)
    print('Extensions successfully loaded.')

bot.run(os.getenv('TOKEN'), bot=True, reconnect=True)
