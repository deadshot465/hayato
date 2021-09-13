import json
import typing

import hikari
from commands.rails.rails import Rails
from lightbulb import slash_commands
from utils.constants import HAYATO_COLOR
from utils.utils import get_author_name


@Rails.subgroup()
class Shinkansen(slash_commands.SlashSubGroup):
    description: str = 'Randomly get or query information on a Shinkansen line or a vehicle used in Shinkansen.'


@Shinkansen.subcommand()
class Line(slash_commands.SlashSubCommand):
    description: str = 'Randomly get or query information on a Shinkansen line.'
    line_name: typing.Optional[str] = \
        slash_commands.Option('The Shinkansen line name you want to ask about. Type "info" or "list" to see'
                              ' more.')

    _path = 'assets/rails/shinkansen.json'
    _formal_name = 'Shinkansen'
    _short_name = 'Shinkansen'
    _footer_name = 'the Shinkansen'
    _color = HAYATO_COLOR

    def __init__(self, bot):
        super().__init__(bot)
        with open(self._path, 'r', encoding='utf-8') as file:
            self.lines: list[dict] = json.loads(file.read())

    def __get_info_embed(self, author_name: str, author_avatar_url: str) -> hikari.Embed:
        return Rails \
            .build_general_embed(author_name=author_name,
                                 author_avatar_url=author_avatar_url,
                                 title=self._formal_name,
                                 color=self._color,
                                 description='The Shinkansen (Japanese: 新幹線), colloquially known in English as the'
                                             ' bullet train, is a network of high-speed railway lines in Japan.'
                                             ' Initially, it was built to connect distant Japanese regions with Tokyo,'
                                             ' the capital, in order to aid economic growth and development. Beyond'
                                             ' long-distance travel, some sections around the largest'
                                             ' metropolitan areas are used as a commuter rail network. It is operated'
                                             ' by five Japan Railways Group companies. Over the Shinkansen\'s 50-plus'
                                             ' year history, carrying over 10 billion passengers, there has not been a'
                                             ' single passenger fatality or injury due to train accidents.',
                                 footer_name=self._footer_name)

    def __get_list_embed(self, author_name: str, author_avatar_url: str, line_list: str) \
            -> hikari.Embed:
        return Rails.build_general_embed(author_name=author_name,
                                         author_avatar_url=author_avatar_url,
                                         title=self._short_name,
                                         color=self._color,
                                         description='Here is a list of lines in %s:\n\n%s' %
                                                     (self._short_name, line_list),
                                         footer_name=self._footer_name)

    async def callback(self, context) -> None:
        author_name = get_author_name(context.author, context.member)
        author_avatar_url = str(context.author.avatar_url) or str(context.author.default_avatar_url)
        if context.option_values.line_name == 'info':
            embed = self.__get_info_embed(author_name, author_avatar_url)
        elif context.option_values.line_name == 'list':
            line_list = list(map(lambda l: l['name'] + ' Shinkansen', self.lines))
            line_list.sort()
            embed = self.__get_list_embed(author_name, author_avatar_url, '\n'.join(line_list))
        elif context.option_values.line_name is None:
            line = Rails.get_random_line(self.lines)
            embed = Rails.build_single_result_embed(author_name, author_avatar_url, line,
                                                    self._footer_name, '%s Shinkansen' % line['name'])
        else:
            embed = Rails.search_line(author_name, author_avatar_url, self._color,
                                      context.option_values.line_name, self.lines, self._short_name,
                                      self._footer_name, '%s Shinkansen')
        await context.respond(embed)


@Shinkansen.subcommand()
class Train(slash_commands.SlashSubCommand):
    description: str = 'Randomly get or query information on a vehicle used in Shinkansen.'
    train_name: typing.Optional[str] = \
        slash_commands.Option('The Shinkansen vehicle name you want to ask about. Type "list" to see all available'
                              ' trains.')

    _path = 'assets/rails/shinkansen_vehicles.json'
    _short_name = 'Shinkansen Trains'
    _footer_name = 'the Shinkansen'
    _display_name = 'Shinkansen %s Series'
    _color = HAYATO_COLOR

    def __init__(self, bot):
        super().__init__(bot)
        with open(self._path, 'r', encoding='utf-8') as file:
            self.trains: list[dict] = json.loads(file.read())

    def __get_list_embed(self, author_name: str, author_avatar_url: str, train_list: str) \
            -> hikari.Embed:
        return Rails.build_general_embed(author_name=author_name,
                                         author_avatar_url=author_avatar_url,
                                         title=self._short_name,
                                         color=self._color,
                                         description='Here is a list of trains in %s:\n\n%s' %
                                                     (self._short_name, train_list),
                                         footer_name=self._footer_name)

    async def callback(self, context) -> None:
        author_name = get_author_name(context.author, context.member)
        author_avatar_url = str(context.author.avatar_url) or str(context.author.default_avatar_url)

        if context.option_values.train_name == 'list':
            line_list = list(map(lambda t: self._display_name % t['name'], self.trains))
            line_list.sort()
            embed = self.__get_list_embed(author_name, author_avatar_url, '\n'.join(line_list))
        elif context.option_values.train_name is None:
            train = Rails.get_random_line(self.trains)
            embed = Rails.build_single_result_embed(author_name, author_avatar_url, train,
                                                    self._footer_name, self._display_name % train['name'])
        else:
            embed = Rails.search_line(author_name, author_avatar_url, self._color,
                                      context.option_values.train_name, self.trains, self._short_name,
                                      self._footer_name, self._display_name,
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
        await context.respond(embed)
