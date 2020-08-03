from discord.ext import commands
import json
import random
import discord
import typing


def parse_hex_colour(hex: str) -> typing.Tuple[int, int, int]:
    r = hex[0:2]
    g = hex[2:4]
    b = hex[4:6]
    return int(r, 16), int(g, 16), int(b, 16)

class HK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        with open('Storage/mtr.json', 'r', encoding='utf-8') as file:
            raw_mtrlines = file.read()
            self.mtrlines: typing.List[object] = json.loads(raw_mtrlines)

    @commands.command(description='Randomly get or query information on an MTR Line.', help='This command will randomly show information on an MTR line, or specific line when it\'s specified.', aliases=['hkmtr'])
    async def mtr(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        author: discord.User = ctx.author
        if specific == '':
            line = random.choice(self.mtrlines)
        elif specific == 'info':
            embed = discord.Embed(color=discord.Color.from_rgb(157, 33, 51),
                                  title='MTR',
                                  description='The Mass Transit Railway (MTR; Chinese: 港鐵) is a major public transport network serving Hong Kong. Operated by the MTR Corporation Limited (MTRCL), it consists of heavy rail, light rail, and feeder bus service centred on an 11-line rapid transit network serving the urbanised areas of Hong Kong Island, Kowloon, and the New Territories. The system included 230.9 km of rail in 2018 with 163 stations. The MTR was ranked the number one metro system in the world by CNN in 2017.\n \nThe MTR system is a common mode of public transport in Hong Kong, with over five million trips made in an average weekday. It consistently achieves a 99.9 per cent on-time rate on its train journeys. As of 2018, the MTR has a 49.3 per cent market share of the franchised public transport market, making it the most popular transport option in Hong Kong. The integration of the Octopus smart card fare-payment technology into the MTR system in September 1997 has further enhanced the ease of commuting on the MTR.')
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/734604988717858846/739961151005130882/MTR.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the MTR!')
            await ctx.send(embed=embed)
            return
        elif specific == 'list':
            line_list = []
            for item in self.mtrlines:
                if item['name'] == 'Airport Express':
                    line_list.append(item['name'])
                else:
                    line_list.append(item['name'] + ' Line')
                line_list.sort()
            line_list_str = ''
            for item in line_list:
                line_list_str = line_list_str + item + '\n'
            embed = discord.Embed(color=discord.Color.from_rgb(157, 33, 51),
                                  title='MTR',
                                  description='Here is a list of lines in the MTR:\n \n' + line_list_str)
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/734604988717858846/739961151005130882/MTR.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the MTR!')
            await ctx.send(embed=embed)
            return
        else:
            first_letter = specific[0].upper()
            specific = first_letter + specific[1:]
            count = 0
            found = False
            for item in self.mtrlines:
                if specific in item['name'] or item['name'] in specific or specific == item['abbrev']:
                    line = item
                    found = True
                count += 1
                if count == len(self.mtrlines) and found == False:
                    await ctx.send("There is no such line in the MTR!")
        colour = parse_hex_colour(line['colour'])
        embed = discord.Embed(color=discord.Color.from_rgb(colour[0], colour[1], colour[2]),
                              title=line['name'] + ' Line', description=line['overview'], )
        embed.set_image(url=line['image'])
        embed.add_field(name='Route', value=line['route'], inline=False)
        embed.add_field(name='Stations', value=line['stations'], inline=True)
        embed.add_field(name='Running time (mins)', value=line['running_time (mins)'], inline=True)
        embed.add_field(name='Length (km)', value=line['length (km)'], inline=True)
        embed.add_field(name='Track Gauge (mm)', value=line['gauge (mm)'], inline=True)
        embed.add_field(name='Train formation', value=line['train_formation'], inline=True)
        embed.add_field(name='Rolling stock', value=line['rolling stock'], inline=True)
        embed.add_field(name='Opened', value=line['opened'], inline=True)
        embed.add_field(name='Daily ridership', value=line['daily_ridership'], inline=True)
        embed.set_footer(text='Ride the MTR!')
        embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(HK(bot))