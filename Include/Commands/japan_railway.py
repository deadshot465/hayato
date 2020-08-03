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


class JapanRailway(commands.Cog):
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

    @commands.command(description='Randomly get or query information on a vehicle.', help='This command will randomly show information on a vehicle, or specific vehicle when it\'s specified.', aliases=['shinkansen', 'ressha'])
    async def train(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        author: discord.User = ctx.author
        if specific == '':
            train = random.choice(self.trains)
        else:
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
        if specific == '':
            line = random.choice(self.metrolines)
        elif specific == 'info':
            embed = discord.Embed(color=discord.Color.from_rgb(20, 157, 211),
                                  title='Tokyo Metro', description='The Tokyo Metro is a major rapid transit system in Tokyo, Japan. While it is not the only rapid transit system operating in Tokyo, it has the higher ridership among the two subway operators: in 2014, the Tokyo Metro had an average daily ridership of 6.84 million passengers, with 9 lines and 180 stations.\n \n Tokyo Metro is operated by Tokyo Metro Co., Ltd., a private company jointly owned by the Japanese government (through the Ministry of Finance) and the Tokyo metropolitan government.')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034/Tokyo_Metro.png')
            embed.set_author(name=str(author.display_name), icon_url=str(author.avatar_url))
            embed.set_footer(text='Ride the Tokyo Metro!')
            await ctx.send(embed=embed)
            return
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


def setup(bot: commands.Bot):
    bot.add_cog(JapanRailway(bot))