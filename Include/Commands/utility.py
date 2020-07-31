from discord.ext import commands
from typing import Tuple
import random


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


# Convert fahrenheit to celsius
def cvt(unit1: str, unit2: str, value: float) -> Tuple[float, float, str, str]:
    target = 0.0
    unit_source = ''
    unit_target = ''
    if unit1 == 'f' and unit2 == 'c':
        target = (value - 32.0) * 5.0 / 9.0
        unit_source = '\u2109'
        unit_target = '\u2103'
    if unit1 == 'c' and unit2 == 'f':
        target = value * 9.0 / 5.0 + 32.0
        unit_source = '\u2103'
        unit_target = '\u2109'
    if unit1 == 'lbs' and unit2 == 'kg':
        target = value / 2.2
        unit_source = 'lbs'
        unit_target = 'kg'
    if unit1 == 'kg' and unit2 == 'lbs':
        target = value * 2.2
        unit_source = 'kg'
        unit_target = 'lbs'
    if unit1 == 'inch' and unit2 == 'cm':
        target = value * 2.54
        unit_source = 'inch'
        unit_target = 'cm'
    if unit1 == 'cm' and unit2 == 'inch':
        target = value / 2.54
        unit_source = 'cm'
        unit_target = 'inch'
    return value, target, unit_source, unit_target


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


class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def vowels(self, ctx: commands.Context, *, args: str):
        answer = count_vowels(args)
        await ctx.send('There are {} vowels in the input!'.format(answer))

    @commands.command()
    async def dashsep(self, ctx: commands.Context, *, args: str):
        answer = dash_separator(args)
        await ctx.send(answer)

    @commands.command()
    async def cvt(self, ctx: commands.Context, unit1: str, unit2: str, value: float):
        answer = cvt(unit1, unit2, value)
        await ctx.send('{}{} is equal to {}{}!'.format(answer[0], answer[2], answer[1], answer[3]))

    @commands.command()
    async def pick(self, ctx: commands.Context, *, args: str):
        answer = pick(args)
        await ctx.send(answer)


def setup(bot: commands.Bot):
    bot.add_cog(UtilityCog(bot))
