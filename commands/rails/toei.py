import json

import hikari
import lightbulb

from commands.rails import rails
from utils.utils import get_author_name

__path = 'assets/rails/toei_subway.json'
__thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/739495626638753792/Toei.png'
__formal_name = 'Toei Subway'
__short_name = __formal_name
__footer_name = 'the Toei Subway'
__color = hikari.Color.of(0x1f8f2f)

with open(__path, 'r', encoding='utf-8') as file:
    __lines: list[dict] = json.loads(file.read())


def __get_info_embed(author_name: str, author_avatar_url: str) -> hikari.Embed:
    return rails \
        .build_general_embed(author_name=author_name,
                             author_avatar_url=author_avatar_url,
                             title=__formal_name,
                             color=__color,
                             description='The Toei Subway is one of two rapid transit systems which make up the '
                                         'Tokyo subway system, the other being Tokyo Metro. It is operated by the '
                                         'Tokyo Metropolitan Government which operates public transport services'
                                         ' in Tokyo. In 2014, the Toei Subway had an average daily ridership of'
                                         ' 6.84 million passengers, with 4 lines and 106 stations.\n\nTokyo Metro'
                                         ' and Toei trains form completely separate networks. While users of'
                                         ' prepaid rail passes can freely interchange between the two networks,'
                                         ' regular ticket holders must purchase a second ticket, or a special'
                                         ' transfer ticket, to change from a Toei line to a Tokyo Metro line and'
                                         ' vice versa.',
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
@lightbulb.option('line_name', 'The Toei Subway line name you want to ask about. Type "info" or "list" to see more.',
                  required=False)
@lightbulb.command('toei', 'Randomly get or query information on a Toei Subway line.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def toei(ctx: lightbulb.Context) -> None:
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
                                                __footer_name, 'Toei %s Line' % line['name'])
    else:
        embed = rails.search_line(author_name, author_avatar_url, __color,
                                  ctx.options.line_name, __lines, __short_name,
                                  __footer_name, 'Toei %s Line')
    await ctx.respond(embed)
