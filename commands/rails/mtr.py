import json

import hikari
import lightbulb

from commands.rails import rails
from utils.utils import get_author_name

__path = 'assets/rails/mtr.json'
__thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/739961151005130882/MTR.png'
__formal_name = 'MTR'
__short_name = __formal_name
__footer_name = 'the MTR'
__color = hikari.Color.of(0x9d2133)

with open(__path, 'r', encoding='utf-8') as file:
    __lines: list[dict] = json.loads(file.read())


def __get_info_embed(author_name: str, author_avatar_url: str) -> hikari.Embed:
    return rails \
        .build_general_embed(author_name=author_name,
                             author_avatar_url=author_avatar_url,
                             title=__formal_name,
                             color=__color,
                             description='The Mass Transit Railway (MTR; Chinese: 港鐵) is a major public transport'
                                         ' network serving Hong Kong. Operated by the MTR Corporation Limited'
                                         ' (MTRCL), it consists of heavy rail, light rail, and feeder bus service'
                                         ' centred on an 11-line rapid transit network serving the urbanised areas'
                                         ' of Hong Kong Island, Kowloon, and the New Territories. The system'
                                         ' included 230.9 km of rail in 2018 with 163 stations. The MTR was ranked'
                                         ' the number one metro system in the world by CNN in 2017.\n\nThe MTR'
                                         ' system is a common mode of public transport in Hong Kong, with over'
                                         ' five million trips made in an average weekday. It consistently achieves'
                                         ' a 99.9 per cent on-time rate on its train journeys. As of 2018, the MTR'
                                         ' has a 49.3 per cent market share of the franchised public transport'
                                         ' market, making it the most popular transport option in Hong Kong.'
                                         ' The integration of the Octopus smart card fare-payment technology into'
                                         ' the MTR system in September 1997 has further enhanced the ease of'
                                         ' commuting on the MTR.',
                             footer_name=__footer_name,
                             thumbnail=__thumbnail)


def __get_list_embed(author_name: str, author_avatar_url: str, line_list: str) \
        -> hikari.Embed:
    return rails.build_general_embed(author_name=author_name,
                                     author_avatar_url=author_avatar_url,
                                     title=__short_name,
                                     color=__color,
                                     description='Here is a list of lines in the %s:\n\n%s' %
                                                 (__short_name, line_list),
                                     footer_name=__footer_name,
                                     thumbnail=__thumbnail)


@rails.rails.child
@lightbulb.option('line_name', 'The MTR line name you want to ask about. Type "info" or "list" to see more.',
                  required=False)
@lightbulb.command('mtr', 'Randomly get or query information on an MTR Line.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def mtr(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    author_avatar_url = str(ctx.author.avatar_url) or str(ctx.author.default_avatar_url)

    if ctx.options.line_name == 'info':
        embed = __get_info_embed(author_name, author_avatar_url)
    elif ctx.options.line_name == 'list':
        line_list = list(map(lambda l: l['name'] + ' Line', __lines))
        line_list.sort()
        embed = __get_list_embed(author_name, author_avatar_url, '\n'.join(line_list))
    elif ctx.options.line_name is None:
        line = rails.get_random_line(__lines)
        embed = rails.build_single_result_embed(author_name, author_avatar_url, line,
                                                __footer_name, line['name'] + ' Line')
    else:
        embed = rails.search_line(author_name, author_avatar_url, __color,
                                  ctx.options.line_name, __lines, __short_name,
                                  __footer_name, '%s Line')
    await ctx.respond(embed)
