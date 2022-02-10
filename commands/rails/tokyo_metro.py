import json

import hikari
import lightbulb

from commands.rails import rails
from utils.utils import get_author_name

__path = 'assets/rails/tokyo_metro.json'
__thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034/Tokyo_Metro.png'
__formal_name = 'Tokyo Metro'
__short_name = __formal_name
__footer_name = 'the Tokyo Metro'
__color = hikari.Color.of(0x149dd3)

with open(__path, 'r', encoding='utf-8') as file:
    __lines: list[dict] = json.loads(file.read())


def __get_info_embed(author_name: str, author_avatar_url: str) -> hikari.Embed:
    return rails \
        .build_general_embed(author_name=author_name,
                             author_avatar_url=author_avatar_url,
                             title=__formal_name,
                             color=__color,
                             description='The Tokyo Metro is a major rapid transit system in Tokyo, Japan. While it'
                                         ' is not the only rapid transit system operating in Tokyo, it has the '
                                         'higher ridership among the two subway operators: in 2014, the Tokyo Metro'
                                         ' had an average daily ridership of 6.84 million passengers, with 9 lines'
                                         ' and 180 stations.\n\n Tokyo Metro is operated by Tokyo Metro Co., Ltd.,'
                                         ' a private company jointly owned by the Japanese government (through the'
                                         ' Ministry of Finance) and the Tokyo metropolitan government.',
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
@lightbulb.option('line_name', 'The Tokyo Metro line name you want to ask about. Type "info" or "list" to see more.',
                  required=False)
@lightbulb.command('tokyo_metro', 'Randomly get or query information on a Tokyo Metro line.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def tokyo_metro(ctx: lightbulb.Context) -> None:
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
                                                __footer_name, 'Tokyo Metro %s Line' % line['name'])
    else:
        embed = rails.search_line(author_name, author_avatar_url, __color,
                                  ctx.options.line_name, __lines, __short_name,
                                  __footer_name, 'Tokyo Metro %s Line')
    await ctx.respond(embed)
