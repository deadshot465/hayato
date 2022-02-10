import json

import hikari
import lightbulb

from commands.rails import rails
from utils.constants import HAYATO_COLOR
from utils.utils import get_author_name

__line_path = 'assets/rails/shinkansen.json'
__line_formal_name = 'Shinkansen'
__line_short_name = 'Shinkansen'
__line_footer_name = 'the Shinkansen'
__line_color = HAYATO_COLOR

__train_path = 'assets/rails/shinkansen_vehicles.json'
__train_short_name = 'Shinkansen Trains'
__train_footer_name = 'the Shinkansen'
__train_display_name = 'Shinkansen %s Series'
__train_color = HAYATO_COLOR

with open(__line_path, 'r', encoding='utf-8') as file:
    __shinkansen_lines: list[dict] = json.loads(file.read())

with open(__train_path, 'r', encoding='utf-8') as file:
    __trains: list[dict] = json.loads(file.read())


def __get_line_info_embed(author_name: str, author_avatar_url: str) -> hikari.Embed:
    return rails \
        .build_general_embed(author_name=author_name,
                             author_avatar_url=author_avatar_url,
                             title=__line_formal_name,
                             color=__line_color,
                             description='The Shinkansen (Japanese: 新幹線), colloquially known in English as the'
                                         ' bullet train, is a network of high-speed railway lines in Japan.'
                                         ' Initially, it was built to connect distant Japanese regions with Tokyo,'
                                         ' the capital, in order to aid economic growth and development. Beyond'
                                         ' long-distance travel, some sections around the largest'
                                         ' metropolitan areas are used as a commuter rail network. It is operated'
                                         ' by five Japan Railways Group companies. Over the Shinkansen\'s 50-plus'
                                         ' year history, carrying over 10 billion passengers, there has not been a'
                                         ' single passenger fatality or injury due to train accidents.',
                             footer_name=__line_footer_name)


def __get_line_list_embed(author_name: str, author_avatar_url: str, line_list: str) \
        -> hikari.Embed:
    return rails.build_general_embed(author_name=author_name,
                                     author_avatar_url=author_avatar_url,
                                     title=__line_short_name,
                                     color=__line_color,
                                     description='Here is a list of lines in %s:\n\n%s' %
                                                 (__line_short_name, line_list),
                                     footer_name=__line_footer_name)


def __get_train_list_embed(author_name: str, author_avatar_url: str, train_list: str) \
        -> hikari.Embed:
    return rails.build_general_embed(author_name=author_name,
                                     author_avatar_url=author_avatar_url,
                                     title=__train_short_name,
                                     color=__train_color,
                                     description='Here is a list of trains in %s:\n\n%s' %
                                                 (__train_short_name, train_list),
                                     footer_name=__train_footer_name)


@rails.rails.child
@lightbulb.command('shinkansen',
                   'Randomly get or query information on a Shinkansen line or a vehicle used in Shinkansen.')
@lightbulb.implements(lightbulb.SlashSubGroup)
async def shinkansen(ctx: lightbulb.Context) -> None:
    pass


@shinkansen.child
@lightbulb.option('line_name', 'The Shinkansen line name you want to ask about. Type "info" or "list" to see'
                               ' more.', required=False)
@lightbulb.command('line', 'Randomly get or query information on a Shinkansen line.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def line(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    author_avatar_url = str(ctx.author.avatar_url) or str(ctx.author.default_avatar_url)
    if ctx.options.line_name == 'info':
        embed = __get_line_info_embed(author_name, author_avatar_url)
    elif ctx.options.line_name == 'list':
        line_list = list(map(lambda l: l['name'] + ' Shinkansen', __shinkansen_lines))
        line_list.sort()
        embed = __get_line_list_embed(author_name, author_avatar_url, '\n'.join(line_list))
    elif ctx.options.line_name is None:
        random_line = rails.get_random_line(__shinkansen_lines)
        embed = rails.build_single_result_embed(author_name, author_avatar_url, random_line,
                                                __line_footer_name, '%s Shinkansen' % random_line['name'])
    else:
        embed = rails.search_line(author_name, author_avatar_url, __line_color,
                                  ctx.options.line_name, __shinkansen_lines, __line_short_name,
                                  __line_footer_name, '%s Shinkansen')
    await ctx.respond(embed)


@shinkansen.child
@lightbulb.option('train_name', 'The Shinkansen vehicle name you want to ask about. Type "list" to see all available'
                                ' trains.', required=False)
@lightbulb.command('train', 'Randomly get or query information on a vehicle used in Shinkansen.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def train(ctx: lightbulb.Context) -> None:
    author_name = get_author_name(ctx.author, ctx.member)
    author_avatar_url = str(ctx.author.avatar_url) or str(ctx.author.default_avatar_url)

    if ctx.options.train_name == 'list':
        line_list = list(map(lambda t: __train_display_name % t['name'], __trains))
        line_list.sort()
        embed = __get_train_list_embed(author_name, author_avatar_url, '\n'.join(line_list))
    elif ctx.options.train_name is None:
        random_train = rails.get_random_line(__trains)
        embed = rails.build_single_result_embed(author_name, author_avatar_url, random_train,
                                                __train_footer_name, __train_display_name % random_train['name'])
    else:
        embed = rails.search_line(author_name, author_avatar_url, __train_color,
                                  ctx.options.train_name, __trains, __train_short_name,
                                  __train_footer_name, __train_display_name,
                                  keyword_limit=0)

    try:
        generator = (i for i, v in enumerate(embed.fields) if v.name == 'Length (km)')
        length_field_index = next(generator)
        embed.edit_field(length_field_index, 'Train Length (m)')
        generator = (i for i, v in enumerate(embed.fields) if v.name == 'Maximum Speed')
        speed_field_index = next(generator)
        embed.edit_field(speed_field_index, inline=False)
    except StopIteration:
        pass
    except AttributeError:
        pass
    embed.set_footer(text='Why not try to ride %s?' % embed.title)
    await ctx.respond(embed)
