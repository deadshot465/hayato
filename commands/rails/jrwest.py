import json

import hikari
import lightbulb

from commands.rails import rails
from utils.utils import get_author_name

__path = 'assets/rails/jrwest.json'
__thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/741817325732233268/JR_West.png'
__formal_name = 'West Japan Railway Company'
__short_name = 'JR West'
__footer_name = 'JR West'
__color = hikari.Color.of(0x0473bd)

with open(__path, 'r', encoding='utf-8') as file:
    __lines: list[dict] = json.loads(file.read())


def __get_info_embed(author_name: str, author_avatar_url: str) -> hikari.Embed:
    return rails \
        .build_general_embed(author_name=author_name,
                             author_avatar_url=author_avatar_url,
                             title=__formal_name,
                             color=__color,
                             description='West Japan Railway Company (西日本旅客鉄道株式会社, Nishi-Nihon Ryokaku Tetsudō '
                                         'Kabushiki-gaisha), also referred to as JR-West '
                                         '(JR西日本, Jeiāru Nishi-Nihon), is one of the Japan Railways Group'
                                         ' (JR Group) companies and operates in western '
                                         'Honshu. It has its headquarters in Kita-ku, Osaka.',
                             footer_name=__footer_name,
                             thumbnail=__thumbnail)


def __get_list_embed(author_name: str, author_avatar_url: str, line_list: str) \
        -> hikari.Embed:
    return rails.build_general_embed(author_name=author_name,
                                     author_avatar_url=author_avatar_url,
                                     title=__short_name,
                                     color=__color,
                                     description='Here is a list of lines in %s:\n\n%s' %
                                                 (__short_name, line_list),
                                     footer_name=__footer_name,
                                     thumbnail=__thumbnail)


@rails.rails.child
@lightbulb.option('line_name', 'The JR West line name you want to ask about. Type "info" or "list" to see more.',
                  required=False)
@lightbulb.command('jr_west', 'Randomly get or query information on JR West Line.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def jr_west(ctx: lightbulb.Context) -> None:
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
