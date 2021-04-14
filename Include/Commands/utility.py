import asyncio
import base64
import json
import random
import re
import requests
import typing

from discord.ext import commands
from typing import Optional, Tuple
from Utils.utils import search_user
from Utils.rapid_api import *


# Available domains.
DOMAINS = {'com', 'net', 'hk', 'org', 'ca', 'info'}

with open('Storage/convert.json', 'r', encoding='utf-8') as file:
    raw_convert_table = file.read()
    convert_table: typing.Dict[object, object] = json.loads(raw_convert_table)


# Count vowels
def count_vowels(string: str) -> int:
    count = 0
    for letter in string:
        if letter in 'AEIOUaeiou':
            count += 1
    return count


# Dash separator
def dash_separator(string: str) -> str:
    """
    (str) -> str
    Returns a string the separates each letter of the input string with a dash.

    >>> dash_separator('hello')
    h-e-l-l-o
    >>> Kirito
    K-i-r-i-t-o
    """
    result = ''
    i = 0
    while i < len(string) - 1:
        result = result + string[i] + '-'
        i += 1
    result += string[i]
    return result


def cvt_units(unit1: str, unit2: str, value: float):
    # Convert temperature units
    output = 0.0
    error = False
    unit_source = ''
    unit_target = ''
    if unit1 == 'c':
        unit_source = '\u2103'
        if unit1 == unit2:
            output = value
            unit_target = unit_source
        elif unit2 == 'k':
            output = value + 273.15
            unit_target = 'K'
        elif unit2 == 'f':
            output = value * 9 / 5 + 32
            unit_target = '\u2109'
        else:
            error = True
    elif unit1 == 'f':
        unit_source = '\u2109'
        if unit1 == unit2:
            output = value
            unit_target = unit_source
        else:
            output = (value - 32) * 5 / 9
            if unit2 == 'c':
                unit_target = '\u2103'
            elif unit2 == 'k':
                output = value + 273.15
                unit_target = 'K'
            else:
                error = True
    elif unit1 == 'k':
        unit_source = 'K'
        if unit1 == unit2:
            output = value
            unit_source = unit_target
        else:
            output = value - 273.15
            if unit2 == 'c':
                unit_target = '\u2103'
            elif unit2 == 'f':
                output = value * 9 / 5 + 32
                unit_target = '\u2109'
            else:
                error = True
    elif unit1 == 'g':
        unit_source = unit1
        if unit1 == unit2:
            output = value
            unit_target = unit_source
        elif unit2 == 'kg':
            output = value * 0.001
            unit_target = 'kg'
        elif unit2 == 'lbs' or unit2 == 'lb':
            output = value * 0.0022
            unit_target = 'lbs'
        else:
            error = True
    elif unit1 == 'kg':
        unit_source = unit1
        if unit1 == unit2:
            output = value
            unit_target = unit_source
        elif unit2 == 'g':
            output = value * 1000
            unit_target = 'g'
        elif unit2 == 'lbs' or unit2 == 'lb':
            output = value * 2.2
            unit_target = 'lbs'
        else:
            error = True
    elif unit1 == 'lbs' or unit1 == 'lb':
        unit_source = 'lbs'
        if unit1 == unit2:
            output = value
            unit_target = unit_source
        elif unit2 == 'kg':
            output = value / 2.2
            unit_target = 'kg'
        elif unit2 == 'g':
            output = (value / 2.2) * 1000
            unit_target = 'g'
        else:
            error = True
    else:
        cvt_factor = convert_table['length'].get(unit2)
        if cvt_factor is None:
            error = True
        else:
            cvt_factor = cvt_factor.get(unit1)
            if cvt_factor is None:
                error = True
            else:
                output = value * cvt_factor
                unit_source = unit1
                unit_target = unit2
    if error:
        return 'The correct usage is `h!cvt <source unit> <target unit> [value=0.0]`!'
    else:
        output = round(output, 2)
        return [value, output, unit_source, unit_target]


# Random pick
def pick(all_choices: str) -> str:
    """
    Input several choices that split with "," and Hayato will help you choose one.
    """
    error = False
    # Separate the choices into a list
    all_choices = all_choices.split(",")
    # For each choice remove the spaces
    for index in range(0, len(all_choices)):
        choice = all_choices[index].strip(" ")
        # If someone tries to fool Hayato, it is impossible
        if choice == "":
            error = True
            break
        # Replace the choice with the no-blank-space one
        all_choices[index] = choice
    # Pick a random choice from the list
    hayato_choice = random.choice(all_choices)
    # return the choice
    if error:
        return "Are you trying to fool me?"
    else:
        return "I pick **" + hayato_choice + "** for you!"


def check_name_or_host(input_string: str) -> bool:
    '''
    (str) -> bool

    Return True if the name or host obeys the following rules:
    - NAME, HOST cannot contain any of {(, ), @, space}
    - NAME, HOST must be in between 1 and 100 characters
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


def verifyemail(email: str) -> str:
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
        return 'This email is not plausible!'
    else:
        return 'This email is plausible!'


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.emote_regex = re.compile(r'(<a?:\w+:\d+>)')
        self.emote_id_regex = re.compile(r'[^:]+(?=>)')
        self.emote_is_animated_regex = re.compile(r'(<a)')
        self.emote_base_link = 'https://cdn.discordapp.com/emojis/'

    @commands.command(description='Count the number of vowels in the input.',
                      help='Count the total number of vowels in a word or a sentence.', aliases=['vowel'])
    async def vowels(self, ctx: commands.Context, *, args: str):
        answer = count_vowels(args)
        await ctx.send('There are {} vowels in the input!'.format(answer))

    @commands.command(description='Separate every letter of your input with a dash.',
                      help='Type in a word or sentence, and let Hayato separate each letter with a dash.',
                      aliases=['separate'])
    async def dashsep(self, ctx: commands.Context, *, args: str):
        # async def dashsep(self, ctx: commands.Context, args: str):
        # h!dashsep Hello, World, Marco is cute. -> Hello,
        answer = dash_separator(args)
        await ctx.send(answer)

    @commands.command(description='Convert units.',
                      help='This command will help you convert between units of temperature, length and weight.',
                      aliases=['convert'])
    async def cvt(self, ctx: commands.Context, unit1: str, unit2: str, value: typing.Optional[float] = 0.0):
        answer = cvt_units(unit1, unit2, value)
        if isinstance(answer, str):
            await ctx.send(answer)
        elif isinstance(answer, list):
            await ctx.send('{}{} is equal to {}{}!'.format(answer[0], answer[2], answer[1], answer[3]))

    @commands.command(description='Hayato will help you pick one choice randomly.',
                      help='Send multiple options to Hayato and let Hayato pick one from those options for you.',
                      aliases=['choose'])
    async def pick(self, ctx: commands.Context, *, args: str):
        answer = pick(args)
        await ctx.send(answer)

    @commands.command(description='Check if the email is plausible.',
                      help='Check if the email address inputted is a plausibly valid email address or not.',
                      aliases=['email'])
    async def verifyemail(self, ctx: commands.Context, *, args: str):
        answer = verifyemail(args)
        await ctx.send(answer)

    @commands.command(description='Enlarge one to multiple emotes.',
                      help='Enlarge one or multiple emotes by getting permanent links of the emotes, to see emotes more clearly or download emotes.',
                      aliases=['emoji'])
    async def enlarge(self, ctx: commands.Context, *, args: typing.Optional[str]):
        if args is None or len(args) == 0:
            await ctx.send("Sorry, but you need to provide me an emote or avatar to use this command~!")
            return
        member = search_user(ctx, args)
        if len(member) > 0:
            await ctx.send('{}, Here ya go~!'.format(ctx.author.mention))
            await ctx.send(member[0].avatar_url)
            return
        result = self.emote_regex.search(args)
        if result is None:
            await ctx.send('Sorry, but you need to provide me an emote to use this command~!')
            return
        split = args.split(' ')
        emote_links = []
        for item in split:
            if self.emote_regex.search(item) is not None:
                for single in self.emote_regex.finditer(item):
                    suffix: str
                    if self.emote_is_animated_regex.search(single.group()) is not None:
                        suffix = '.gif'
                    else:
                        suffix = '.png'
                    emote_id = self.emote_id_regex.search(single.group())
                    emote_links.append(self.emote_base_link + str(emote_id.group()) + suffix)
        if len(emote_links) > 1:
            await ctx.send('{}, here are your requested emotes!'.format(ctx.author.mention))
        else:
            await ctx.send('{}, here is your requested emote!'.format(ctx.author.mention))
        for link in emote_links:
            await ctx.send(link)

    @commands.command(description='Let Hayato evaluate your Python code.',
                      help='Ask for help from Hayato in evaluating your Pytho code.')
    async def eval(self, ctx: commands.Context, *, content: str):
        header = generate_auth_header('judge0-ce.p.rapidapi.com')
        code = content.split('\n')
        split = code[1:len(code) - 1]
        actual_code = '\n'.join(split)
        request_data = {
            'language_id': PYTHON_LANG_ID,
            'source_code': str(base64.b64encode(actual_code.encode('utf8'))).lstrip('b\'')
        }
        query_string = {
            'base64_encoded': 'true',
            'fields': '*'
        }
        request = requests.request('POST', SUBMISSION_URL, headers=header, data=json.dumps(request_data),
                                   params=query_string)
        print(f'{request.status_code}')
        token: str = json.loads(request.text)['token']

        async def loop():
            while (await get_eval_result(header, token, ctx)) is not True:
                continue

        await asyncio.create_task(loop())

    @commands.command(description='Get the avatar of yourself or another member in the guild.',
                      help='Get the avatar of yourself or another member in the guild. Supported search patterns '
                           'include searching by pinging, user tag, user id, and partial user names.',
                      aliases=['pfp'])
    async def avatar(self, ctx: commands.Context, user: Optional[str] = ''):
        if user is None or len(user) == 0:
            await ctx.send('{}, here is your personal avatar!'.format(ctx.author.mention))
            await ctx.send(ctx.author.avatar_url)
            return
        member = search_user(ctx, user)
        if len(member) == 0:
            await ctx.send('{} Sorry, but I can\'t find that user'.format(ctx.author.mention))
            return
        await ctx.send('{}, here is {}\'s avatar!'.format(ctx.author.mention, member[0].display_name))
        await ctx.send(member[0].avatar_url)


def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))
