from discord.ext import commands
import json
import random
import discord
import typing


# Convert colour in hex to dec
def parse_hex_colour(hex: str) -> typing.Tuple[int, int, int]:
    r = hex[0:2]
    g = hex[2:4]
    b = hex[4:6]
    return int(r, 16), int(g, 16), int(b, 16)


class Rails(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        with open('Storage/trains.json', 'r', encoding='utf-8') as file:
            raw_trains = file.read()
            self.trains: typing.List[object] = json.loads(raw_trains)
        with open('Storage/tokyo_metro.json', 'r', encoding='utf-8') as file_2:
            raw_metrolines = file_2.read()
            self.metrolines: typing.List[object] = json.loads(raw_metrolines)
        with open('Storage/toei_subway.json', 'r', encoding='utf-8') as file_3:
            raw_toeilines = file_3.read()
            self.toeilines: typing.List[object] = json.loads(raw_toeilines)
        with open('Storage/mtr.json', 'r', encoding='utf-8') as file_4:
            raw_mtrlines = file_4.read()
            self.mtrlines: typing.List[object] = json.loads(raw_mtrlines)

    @commands.command(description='Randomly get or query information on a vehicle.', help='This command will randomly show information on a vehicle, or specific vehicle when it\'s specified.', aliases=['shinkansen', 'ressha'])
    async def train(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        author: discord.User = ctx.author
        # If the user does not specify which train, it will return a random train
        if specific == '':
            train = random.choice(self.trains)
        # Return a list of trains in the database if the user specified "list"
        elif specific == 'list':
            # Add the name of the trains into a list and sort in alphabetical order
            train_list = []
            for item in self.trains:
                train_list.append('Shinkansen ' + item['name'] + ' Series')
                train_list.sort()
            train_list_str = ''
            for item in train_list:
                train_list_str = train_list_str + item + '\n'
            embed = discord.Embed(color=discord.Color.from_rgb(30, 99, 175),
                                  title='Shinkansen Trains',
                                  description='Here is a list of trains in Shinkansen:\n \n' + train_list_str)
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the Shinkansen!')
            await ctx.send(embed=embed)
            return
        else:
            # Search the name of the train
            specific = specific.upper()
            count = 0
            found = False
            for item in self.trains:
                if specific == item['name']:
                    train = item
                    found = True
                count += 1
                if count == len(self.trains) and found == False:
                    await ctx.send("There is no such train information at the moment!")
        colour = parse_hex_colour(train['colour'])
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

    @commands.command(description='Randomly get or query information on a Tokyo Metro line.', help='This command will randomly show information on a Tokyo Metro line, or specific line when it\'s specified.', aliases=['tokyometro'])
    async def metro(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        author: discord.User = ctx.author
        # If the user does not specify which line, it will return a random line
        if specific == '':
            line = random.choice(self.metrolines)
        # Return information about the Tokyo Metro if the user specified "info"
        elif specific == 'info':
            embed = discord.Embed(color=discord.Color.from_rgb(20, 157, 211),
                                  title='Tokyo Metro', description='The Tokyo Metro is a major rapid transit system in Tokyo, Japan. While it is not the only rapid transit system operating in Tokyo, it has the higher ridership among the two subway operators: in 2014, the Tokyo Metro had an average daily ridership of 6.84 million passengers, with 9 lines and 180 stations.\n \n Tokyo Metro is operated by Tokyo Metro Co., Ltd., a private company jointly owned by the Japanese government (through the Ministry of Finance) and the Tokyo metropolitan government.')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034/Tokyo_Metro.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the Tokyo Metro!')
            await ctx.send(embed=embed)
            return
        # Return a list of lines in the database if the user specified "list"
        elif specific == 'list':
            line_list = []
            for item in self.metrolines:
                line_list.append(item['name'] + ' Line')
                line_list.sort()
            line_list_str = ''
            for item in line_list:
                line_list_str = line_list_str + item + '\n'
            embed = discord.Embed(color=discord.Color.from_rgb(20, 157, 211),
                                  title='Tokyo Metro',
                                  description='Here is a list of lines in the Tokyo Metro:\n \n' + line_list_str)
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034/Tokyo_Metro.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the Tokyo Metro!')
            await ctx.send(embed=embed)
            return
        else:
            # Search the name of the line
            first_letter = specific[0].upper()
            specific = first_letter + specific[1:]
            count = 0
            found = False
            for item in self.metrolines:
                if item['name'] in specific or specific == item['abbrev']:
                    line = item
                    found = True
                count += 1
                if count == len(self.metrolines) and found == False:
                    await ctx.send("There is no such line in Tokyo Metro!")
        colour = parse_hex_colour(line['colour'])
        embed = discord.Embed(color=discord.Color.from_rgb(colour[0], colour[1], colour[2]),
                              title='Tokyo Metro ' + line['name'] + ' Line', description=line['overview'], )
        embed.set_image(url=line['image'])
        embed.add_field(name='Route', value=line['route'], inline=False)
        embed.add_field(name='Stations', value=line['stations'], inline=True)
        embed.add_field(name='Length (km)', value=line['length (km)'], inline=True)
        embed.add_field(name='Track Gauge (mm)', value=line['gauge (mm)'], inline=True)
        embed.add_field(name='Train formation', value=line['train_formation'], inline=True)
        embed.add_field(name='Opened', value=line['opened'], inline=True)
        embed.add_field(name='Daily ridership', value=line['daily_ridership'], inline=False)
        embed.set_thumbnail(url=line['logo'])
        embed.set_footer(text='Ride the Tokyo Metro!')
        embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
        await ctx.send(embed=embed)

    @commands.command(description='Randomly get or query information on a Toei Subway line.', help='This command will randomly show information on a Toei Subway line, or specific line when it\'s specified.', aliases=['toeisubway'])
    async def toei(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        author: discord.User = ctx.author
        if specific == '':
            line = random.choice(self.toeilines)
        elif specific == 'info':
            embed = discord.Embed(color=discord.Color.from_rgb(31, 143, 47),
                                  title='Toei Subway', description='The Toei Subway is one of two rapid transit systems which make up the Tokyo subway system, the other being Tokyo Metro. It is operated by the Tokyo Metropolitan Government which operates public transport services in Tokyo. In 2014, the Toei Subway had an average daily ridership of 6.84 million passengers, with 4 lines and 106 stations.\n \nTokyo Metro and Toei trains form completely separate networks. While users of prepaid rail passes can freely interchange between the two networks, regular ticket holders must purchase a second ticket, or a special transfer ticket, to change from a Toei line to a Tokyo Metro line and vice versa.')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/734604988717858846/739495626638753792/Toei.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the Toei Subway!')
            await ctx.send(embed=embed)
            return
        elif specific == 'list':
            line_list = []
            for item in self.toeilines:
                line_list.append(item['name'] + ' Line')
                line_list.sort()
            line_list_str = ''
            for item in line_list:
                line_list_str = line_list_str + item + '\n'
            embed = discord.Embed(color=discord.Color.from_rgb(31, 143, 47),
                                  title='Toei Subway',
                                  description='Here is a list of lines in the Toei Subway:\n \n' + line_list_str)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/734604988717858846/739495626638753792/Toei.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the Toei Subway!')
            await ctx.send(embed=embed)
            return
        else:
            first_letter = specific[0].upper()
            specific = first_letter + specific[1:]
            count = 0
            found = False
            for item in self.toeilines:
                if item['name'] in specific or specific == item['abbrev']:
                    line = item
                    found = True
                count += 1
                if count == len(self.toeilines) and found == False:
                    await ctx.send("There is no such line in Toei Subway!")
        colour = parse_hex_colour(line['colour'])
        embed = discord.Embed(color=discord.Color.from_rgb(colour[0], colour[1], colour[2]),
                              title='Toei ' + line['name'] + ' Line', description=line['overview'], )
        embed.set_image(url=line['image'])
        embed.add_field(name='Route', value=line['route'], inline=False)
        embed.add_field(name='Stations', value=line['stations'], inline=True)
        embed.add_field(name='Length (km)', value=line['length (km)'], inline=True)
        embed.add_field(name='Track Gauge (mm)', value=line['gauge (mm)'], inline=True)
        embed.add_field(name='Opened', value=line['opened'], inline=True)
        embed.add_field(name='Daily ridership', value=line['daily_ridership'], inline=True)
        embed.set_thumbnail(url=line['logo'])
        embed.set_footer(text='Ride the Toei Subway!')
        embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
        await ctx.send(embed=embed)

    @commands.command(description='Randomly get or query information on an MTR Line.',
                      help='This command will randomly show information on an MTR line, or specific line when it\'s specified.',
                      aliases=['hkmtr'])
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
    bot.add_cog(Rails(bot))