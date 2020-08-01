from discord.ext import commands
import json
import random
import discord
import typing


def parse_hex_color(hex: str) -> typing.Tuple[int, int, int]:
    r = hex[0:2]
    g = hex[2:4]
    b = hex[4:6]
    return int(r, 16), int(g, 16), int(b, 16)


class ShinkansenCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        with open('Storage/trains.json', 'r', encoding='utf-8') as file:
            raw_trains = file.read()
            self.trains = json.loads(raw_trains)

    @commands.command()
    async def train(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        author: discord.User = ctx.author
        if specific == '':
            train = random.choice(self.trains)
        else:
            specific = specific.upper()
            for item in self.trains:
                if specific in item['name']:
                    train = item
        colour = parse_hex_color(train['colour'])
        embed = discord.Embed(color=discord.Color.from_rgb(colour[0], colour[1], colour[2]),title='Shinkansen ' + train['name'] + ' Series', description=train['overview'],)
        embed.set_image(url=train['link'])
        embed.add_field(name='Constructed', value=train['constructed'], inline=True)
        embed.add_field(name='Formation', value=train['formation'], inline=True)
        embed.add_field(name='Capacity', value=train['capacity'], inline=False)
        embed.add_field(name='Maximum Speed', value=train['maximum_speed'], inline=False)
        embed.add_field(name='Acceleration', value=train['acceleration'], inline=True)
        embed.add_field(name='Train Length (m)', value=train['length (m)'], inline=True)
        embed.add_field(name='Track Gauge (mm)', value=train['gauge (mm)'], inline=True)
        embed.add_field(name='Lines Served', value=train['lines_served'], inline=False)
        embed.set_footer(text='Why not try to ride Shinkansen ' + train['name'] + ' Series?')
        embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
        await ctx.send(embed=embed)



def setup(bot: commands.Bot):
    bot.add_cog(ShinkansenCog(bot))