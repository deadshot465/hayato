from discord.ext import commands
from similarity.damerau import Damerau
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


# It's generally a bad idea to name the function using the same name.
def get_train(ctx: commands.Context, trains: typing.List[object], specific: typing.Optional[str] = ''):
    author: discord.User = ctx.author
    # If the user does not specify which train, it will return a random train
    if specific == '':
        train = random.choice(trains)
    # Return a list of trains in the database if the user specified "list"
    elif specific == 'list':
        # Add the name of the trains into a list and sort in alphabetical order
        train_list = []
        for item in trains:
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
        return embed
    else:
        # Search the name of the train
        specific = specific.upper()
        count = 0
        found = False
        for item in trains:
            if specific == item['name']:
                train = item
                found = True
            count += 1
            if count == len(trains) and found == False:
                return "There is no such train information at the moment!"
    colour = parse_hex_colour(train['colour'])
    embed = discord.Embed(color=discord.Color.from_rgb(colour[0], colour[1], colour[2]),
                          title='Shinkansen ' + train['name'] + ' Series', description=train['overview'], )
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
    return embed


def get_embed(ctx: commands.Context, title: str, color: discord.Color, description: str, *,
              route: typing.Optional[str] = '', stations: typing.Optional[int] = 0,
              length: typing.Optional[float] = 0.0, track_gauge: typing.Optional[float] = 0.0,
              formation: typing.Optional[str] = '', opened: typing.Optional[str] = '',
              running_time: typing.Optional[str] = '', rolling_stock: typing.Optional[str] = '',
              maximum_speed: typing.Optional[str] = '', ridership: typing.Optional[str] = '',
              operator: typing.Optional[str] = '', image: typing.Optional[str] = '',
              thumbnail: typing.Optional[str] = '', footer_name: typing.Optional[str] = '') -> discord.Embed:
    author: discord.User = ctx.author
    embed = discord.Embed(title=title, color=color, description=description).set_author(name=author.display_name,
                                                                                        icon_url=author.avatar_url)
    if len(route) > 0:
        embed.add_field(name='Route', value=route, inline=False)
    if stations > 0:
        embed.add_field(name='Stations', value=stations, inline=True)
    if len(maximum_speed) > 0:
        embed.add_field(name='Maxiumum Speed', value=maximum_speed, inline=True)
    if length > 0.0:
        embed.add_field(name='Length (km)', value=length, inline=True)
    if track_gauge > 0.0:
        embed.add_field(name='Track Gauge (mm)', value=track_gauge, inline=True)
    if len(formation) > 0:
        embed.add_field(name='Train formation', value=formation, inline=True)
    if len(running_time) > 0:
        embed.add_field(name='Running time (mins)', value=running_time, inline=True)
    if len(opened) > 0:
        embed.add_field(name='Opened', value=opened, inline=True)
    if len(ridership) > 0:
        embed.add_field(name='Daily ridership', value=ridership, inline=True)
    if len(rolling_stock) > 0:
        embed.add_field(name='Rolling stock', value=rolling_stock, inline=False)
    if len(operator):
        embed.add_field(name='Operator', value=operator, inline=False)

    if len(thumbnail) > 0:
        embed.set_thumbnail(url=thumbnail)
    if len(image) > 0:
        embed.set_image(url=image)

    embed.set_footer(text=f'Ride {footer_name}!')
    return embed


def fuzzy_search(ctx: commands.Context, query: str, lines: typing.List[object]) -> typing.Optional[discord.Embed]:
    line_names = list(map(lambda x: x['name'], lines))
    author: discord.User = ctx.author
    damerau = Damerau()

    def check_distance(name: str) -> bool:
        distance = damerau.distance(query, name)
        return distance <= 4.0

    line_names = list(filter(check_distance, line_names))
    if len(line_names) == 0:
        return None
    else:
        embed = discord.Embed(title='Search Result', description='Sorry, I cannot find any results. Did you mean...',
                              color=discord.Color.from_rgb(30, 99, 175)).set_author(name=author.display_name,
                                                                                    icon_url=author.avatar_url)
        joined = '\n'.join(list(map(lambda x: '`{}`'.format(x), line_names)))
        embed.add_field(name='Results', value=joined, inline=False)
        return embed


def get_multiple_result_embed(ctx: commands.Context, lines: typing.List[object]) -> discord.Embed:
    author: discord.User = ctx.author
    embed = discord.Embed(title='Search Result', description='The following are possible search results.', color=discord.Color.from_rgb(30, 99, 175)).set_author(name=author.display_name, icon_url=author.avatar_url)
    line_names = list(map(lambda x: '`{}`'.format(x['name']), lines))
    joined = '\n'.join(line_names)
    embed.add_field(name='Results', value=joined, inline=False)
    return embed


async def search_line(ctx: commands.Context, specific: str, lines: typing.List[dict], railway_name: str) -> typing.Union[typing.Optional[discord.Embed], dict]:
    found = False
    found_lines = []
    line = dict()
    for item in lines:
        if specific == item['abbrev']:
            line = item
            found = True
            break
        specific = specific.lower()
        if specific in item['name'].lower() and len(specific) >= 3:
            line = item
            found_lines.append(item)
            found = True
        elif len(specific) < 3:
            await ctx.send('The keyword has to be at least 3 characters long!')
            return None

    if len(found_lines) > 1:
        embed = get_multiple_result_embed(ctx, found_lines)
        return embed
    elif not found:
        embed = fuzzy_search(ctx, specific, lines)
        if embed is None:
            await ctx.send('There is no such line in {}!'.format(railway_name))
            return None
        return embed
    return line


class Rails(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        with open('Storage/trains.json', 'r', encoding='utf-8') as file:
            raw_trains = file.read()
            self.trains: typing.List[dict] = json.loads(raw_trains)
        with open('Storage/tokyo_metro.json', 'r', encoding='utf-8') as file_2:
            raw_metrolines = file_2.read()
            self.metrolines: typing.List[dict] = json.loads(raw_metrolines)
        with open('Storage/toei_subway.json', 'r', encoding='utf-8') as file_3:
            raw_toeilines = file_3.read()
            self.toeilines: typing.List[dict] = json.loads(raw_toeilines)
        with open('Storage/mtr.json', 'r', encoding='utf-8') as file_4:
            raw_mtrlines = file_4.read()
            self.mtrlines: typing.List[dict] = json.loads(raw_mtrlines)
        with open('Storage/shinkansen.json', 'r', encoding='utf-8') as file_5:
            raw_shinkansen = file_5.read()
            self.shinkansen: typing.List[dict] = json.loads(raw_shinkansen)
        with open('Storage/jrwest.json', 'r', encoding='utf-8') as file_6:
            raw_jrwestlines = file_6.read()
            self.jrwestlines: typing.List[dict] = json.loads(raw_jrwestlines)

    @commands.command(description='Randomly get or query information on a Tokyo Metro line.',
                      help='This command will randomly show information on a Tokyo Metro line, or specific line when it\'s specified.',
                      aliases=['tokyometro'])
    async def metro(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        # If the user does not specify which line, it will return a random line
        line = dict()
        if specific == '':
            line = random.choice(self.metrolines)
        # Return information about the Tokyo Metro if the user specified "info"
        elif specific == 'info':
            embed = get_embed(ctx, 'Tokyo Metro', discord.Color.from_rgb(20, 157, 211),
                              'The Tokyo Metro is a major rapid transit system in Tokyo, Japan. While it is not the '
                              'only rapid transit system operating in Tokyo, it has the higher ridership among the '
                              'two subway operators: in 2014, the Tokyo Metro had an average daily ridership of 6.84 '
                              'million passengers, with 9 lines and 180 stations.\n \n Tokyo Metro is operated by '
                              'Tokyo Metro Co., Ltd., a private company jointly owned by the Japanese government ('
                              'through the Ministry of Finance) and the Tokyo metropolitan government.',
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034'
                                        '/Tokyo_Metro.png',
                              footer_name='the Tokyo Metro')
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
            embed = get_embed(ctx, 'Tokyo Metro', discord.Color.from_rgb(20, 157, 211), 'Here is a list of lines in the Tokyo Metro:\n \n' + line_list_str,
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034'
                                        '/Tokyo_Metro.png',
                              footer_name='the Tokyo Metro')
            await ctx.send(embed=embed)
            return
        else:
            # Search the name of the line
            result = await search_line(ctx, specific, self.metrolines, 'Tokyo Metro')
            if isinstance(result, discord.Embed):
                await ctx.send(embed=result)
                return
            elif isinstance(result, dict):
                line = result
            else:
                return

        colour = parse_hex_colour(line['colour'])
        embed = get_embed(ctx, title='Tokyo Metro ' + line['name'] + ' Line', color=discord.Color.from_rgb(colour[0], colour[1], colour[2]), description=line['overview'],
                          route=line['route'], stations=line['stations'], track_gauge=line['gauge (mm)'],
                          length=line['length (km)'], formation=line['train_formation'], opened=line['opened'],
                          ridership=str(line['daily_ridership']), thumbnail=line['logo'], footer_name='the Tokyo Metro',
                          image=line['image'])
        await ctx.send(embed=embed)

    @commands.command(description='Randomly get or query information on a Toei Subway line.',
                      help='This command will randomly show information on a Toei Subway line, or specific line when it\'s specified.',
                      aliases=['toeisubway'])
    async def toei(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        line = dict()
        if specific == '':
            line = random.choice(self.toeilines)
        elif specific == 'info':
            embed = get_embed(ctx, 'Toei Subway', discord.Color.from_rgb(31, 143, 47),
                              'The Toei Subway is one of two rapid transit systems which make up the Tokyo subway system, the other being Tokyo Metro. It is operated by the Tokyo Metropolitan Government which operates public transport services in Tokyo. In 2014, the Toei Subway had an average daily ridership of 6.84 million passengers, with 4 lines and 106 stations.\n \nTokyo Metro and Toei trains form completely separate networks. While users of prepaid rail passes can freely interchange between the two networks, regular ticket holders must purchase a second ticket, or a special transfer ticket, to change from a Toei line to a Tokyo Metro line and vice versa.',
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/739495626638753792/Toei.png',
                              footer_name='the Toei Subway')
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
            embed = get_embed(ctx, 'Toei Subway', discord.Color.from_rgb(31, 143, 47),
                              'Here is a list of lines in the Toei Subway:\n \n' + line_list_str,
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/739495626638753792/Toei.png',
                              footer_name='the Toei Subway')
            await ctx.send(embed=embed)
            return
        else:
            result = await search_line(ctx, specific, self.toeilines, 'Toei Subway')
            if isinstance(result, discord.Embed):
                await ctx.send(embed=result)
                return
            elif isinstance(result, dict):
                line = result
            else:
                return

        colour = parse_hex_colour(line['colour'])
        embed = get_embed(ctx, title='Toei ' + line['name'] + ' Line',
                          color=discord.Color.from_rgb(colour[0], colour[1], colour[2]), description=line['overview'],
                          route=line['route'], stations=line['stations'], track_gauge=line['gauge (mm)'],
                          length=line['length (km)'], opened=line['opened'],
                          ridership=str(line['daily_ridership']), thumbnail=line['logo'], footer_name='the Toei Subway',
                          image=line['image'])
        await ctx.send(embed=embed)

    @commands.command(description='Randomly get or query information on an MTR Line.',
                      help='This command will randomly show information on an MTR line, or specific line when it\'s specified.',
                      aliases=['hkmtr'])
    async def mtr(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        line = dict()
        if specific == '':
            line = random.choice(self.mtrlines)
        elif specific == 'info':
            embed = get_embed(ctx, 'MTR', discord.Color.from_rgb(157, 33, 51),
                              'The Mass Transit Railway (MTR; Chinese: 港鐵) is a major public transport network serving Hong Kong. Operated by the MTR Corporation Limited (MTRCL), it consists of heavy rail, light rail, and feeder bus service centred on an 11-line rapid transit network serving the urbanised areas of Hong Kong Island, Kowloon, and the New Territories. The system included 230.9 km of rail in 2018 with 163 stations. The MTR was ranked the number one metro system in the world by CNN in 2017.\n \nThe MTR system is a common mode of public transport in Hong Kong, with over five million trips made in an average weekday. It consistently achieves a 99.9 per cent on-time rate on its train journeys. As of 2018, the MTR has a 49.3 per cent market share of the franchised public transport market, making it the most popular transport option in Hong Kong. The integration of the Octopus smart card fare-payment technology into the MTR system in September 1997 has further enhanced the ease of commuting on the MTR.',
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/739961151005130882/MTR.png',
                              footer_name='the MTR')
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
            embed = get_embed(ctx, 'MTR', discord.Color.from_rgb(157, 33, 51),
                              'Here is a list of lines in the MTR:\n \n' + line_list_str,
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/739961151005130882/MTR.png',
                              footer_name='the MTR')
            await ctx.send(embed=embed)
            return
        else:
            result = await search_line(ctx, specific, self.mtrlines, 'MTR')
            if isinstance(result, discord.Embed):
                await ctx.send(embed=result)
                return
            elif isinstance(result, dict):
                line = result
            else:
                return
        colour = parse_hex_colour(line['colour'])
        embed = get_embed(ctx, title=line['name'] + ' Line',
                          color=discord.Color.from_rgb(colour[0], colour[1], colour[2]), description=line['overview'],
                          route=line['route'], stations=line['stations'], track_gauge=line['gauge (mm)'],
                          length=line['length (km)'], opened=line['opened'],
                          running_time=str(line['running_time (mins)']),
                          formation=line['train_formation'],
                          rolling_stock=line['rolling_stock'],
                          ridership=str(line['daily_ridership']), footer_name='the MTR',
                          image=line['image'])
        await ctx.send(embed=embed)

    @commands.command(
        description='Randomly get or query information on a Shinkansen line or a vehicle used in Shinkansen.',
        help='This command will randomly show information on a Shinkansen line or vehicle, or specific line/vehicle when it\'s specified.',
        aliases=['bullettrain'])
    async def shinkansen(self, ctx: commands.Context, arg_1: typing.Optional[str] = '',
                         arg_2: typing.Optional[str] = ''):
        line = dict()
        if arg_1 == '':
            line = random.choice(self.shinkansen)
        elif arg_1 == 'info':
            embed = get_embed(ctx, 'Shinkansen', discord.Color.from_rgb(30, 99, 175),
                              'The Shinkansen (Japanese: 新幹線), colloquially known in English as the bullet train, is a network of high-speed railway lines in Japan. Initially, it was built to connect distant Japanese regions with Tokyo, the capital, in order to aid economic growth and development. Beyond long-distance travel, some sections around the largest metropolitan areas are used as a commuter rail network. It is operated by five Japan Railways Group companies. Over the Shinkansen\'s 50-plus year history, carrying over 10 billion passengers, there has been not a single passenger fatality or injury due to train accidents.',
                              footer_name='the Shinkansen')
            await ctx.send(embed=embed)
            return
        elif arg_1 == 'train':
            embed = get_train(ctx, self.trains, arg_2)
            if isinstance(embed, str):
                await ctx.send(embed)
            elif isinstance(embed, discord.Embed):
                await ctx.send(embed=embed)
            return
        elif arg_1 == 'list':
            line_list = []
            for item in self.shinkansen:
                line_list.append(item['name'] + ' Shinkansen')
                line_list.sort()
            line_list_str = ''
            for item in line_list:
                line_list_str = line_list_str + item + '\n'
            embed = get_embed(ctx, 'Shinkansen', discord.Color.from_rgb(30, 99, 175),
                              'Here is a list of lines in Shinkansen:\n \n' + line_list_str,
                              footer_name='the Shinkansen')
            await ctx.send(embed=embed)
            return
        else:
            # Since Shinkansen doesn't have abbreviations, we have to do it for Shinkansen specifically.
            arg_1 = arg_1.lower()
            found = False
            found_lines = []
            for item in self.shinkansen:
                if arg_1 in item['name'].lower() and len(arg_1) >= 3:
                    line = item
                    found_lines.append(item)
                    found = True
                elif len(arg_1) < 3:
                    await ctx.send('The keyword has to be at least 3 characters long!')
                    return

            if len(found_lines) > 1:
                embed = get_multiple_result_embed(ctx, found_lines)
                await ctx.send(embed=embed)
                return
            elif not found:
                embed = fuzzy_search(ctx, arg_1, self.shinkansen)
                if embed is None:
                    await ctx.send('There is no such line in the Shinkansen!')
                    return
                else:
                    await ctx.send(embed=embed)
                    return

        colour = parse_hex_colour(line['colour'])
        embed = get_embed(ctx, title=line['name'] + ' Shinkansen',
                          color=discord.Color.from_rgb(colour[0], colour[1], colour[2]), description=line['overview'],
                          route=line['route'], stations=line['stations'], track_gauge=line['gauge (mm)'],
                          length=line['length (km)'], opened=line['opened'],
                          rolling_stock=line['rolling_stock'],
                          maximum_speed=line['maximum_speed'],
                          operator=line['operator'],
                          thumbnail=line['icon'], footer_name='the Shinkansen',
                          image=line['image'])
        await ctx.send(embed=embed)

    @commands.command(description='Randomly get or query information on JR West Line.',
                      help='This command will randomly show information on a JR West line, or specific line when it\'s specified.',
                      aliases=['west'])
    async def jrwest(self, ctx: commands.Context, specific: typing.Optional[str] = ''):
        line = dict()
        if specific == '':
            line = random.choice(self.jrwestlines)
        elif specific == 'info':
            embed = get_embed(ctx, 'West Japan Railway Company', discord.Color.from_rgb(4, 115, 189),
                              'West Japan Railway Company (西日本旅客鉄道株式会社, Nishi-Nihon Ryokaku Tetsudō Kabushiki-gaisha), also referred to as JR-West (JR西日本, Jeiāru Nishi-Nihon), is one of the Japan Railways Group (JR Group) companies and operates in western Honshu. It has its headquarters in Kita-ku, Osaka.',
                              footer_name='JR West', thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/741817325732233268/JR_West.png')
            await ctx.send(embed=embed)
            return
        elif specific == 'list':
            line_list = []
            for item in self.jrwestlines:
                line_list.append(item['name'] + ' Line')
                line_list.sort()
            line_list_str = ''
            for item in line_list:
                line_list_str = line_list_str + item + '\n'
            embed = get_embed(ctx, 'JR West', discord.Color.from_rgb(4, 115, 189),
                              'Here is a list of lines in JR West:\n \n' + line_list_str,
                              footer_name='JR West',
                              thumbnail='https://cdn.discordapp.com/attachments/734604988717858846/741817325732233268/JR_West.png')
            await ctx.send(embed=embed)
            return
        else:
            result = await search_line(ctx, specific, self.jrwestlines, 'JR West')
            if isinstance(result, discord.Embed):
                await ctx.send(embed=result)
                return
            elif isinstance(result, dict):
                line = result
            else:
                return
        colour = parse_hex_colour(line['colour'])
        embed = get_embed(ctx, title=line['name'] + ' Line',
                          color=discord.Color.from_rgb(colour[0], colour[1], colour[2]), description=line['overview'],
                          route=line['route'], stations=line['stations'], track_gauge=line['gauge (mm)'],
                          length=line['length (km)'], opened=line['opened'],
                          maximum_speed=line['maximum_speed'],
                          thumbnail=line['logo'], footer_name='JR West',
                          image=line['image'])
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Rails(bot))
