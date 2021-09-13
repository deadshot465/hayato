import json
import typing

import hikari
from commands.rails.rails import Rails
from lightbulb import slash_commands
from utils.utils import get_author_name


@Rails.subcommand()
class Toei(slash_commands.SlashSubCommand):
    description: str = 'Randomly get or query information on a Toei Subway line.'
    line_name: typing.Optional[str] = \
        slash_commands.Option('The Toei Subway line name you want to ask about. Type "info" or "list" to see more.')

    _path = 'assets/rails/toei_subway.json'
    _thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/739495626638753792/Toei.png'
    _formal_name = 'Toei Subway'
    _short_name = _formal_name
    _footer_name = 'the Toei Subway'
    _color = hikari.Color.of(0x1f8f2f)

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
                                 footer_name=self._footer_name,
                                 thumbnail=self._thumbnail)

    def __get_list_embed(self, author_name: str, author_avatar_url: str, line_list: str) \
            -> hikari.Embed:
        return Rails.build_general_embed(author_name=author_name,
                                         author_avatar_url=author_avatar_url,
                                         title=self._short_name,
                                         color=self._color,
                                         description='Here is a list of lines in the %s:\n\n%s' %
                                                     (self._short_name, line_list),
                                         footer_name=self._footer_name,
                                         thumbnail=self._thumbnail)

    async def callback(self, context) -> None:
        author_name = get_author_name(context.author, context.member)
        author_avatar_url = str(context.author.avatar_url) or str(context.author.default_avatar_url)

        if context.option_values.line_name == 'info':
            embed = self.__get_info_embed(author_name, author_avatar_url)
        elif context.option_values.line_name == 'list':
            line_list = list(map(lambda l: l['name'] + ' Line', self.lines))
            line_list.sort()
            embed = self.__get_list_embed(author_name, author_avatar_url, '\n'.join(line_list))
        elif context.option_values.line_name is None:
            line = Rails.get_random_line(self.lines)
            embed = Rails.build_single_result_embed(author_name, author_avatar_url, line,
                                                    self._footer_name, 'Toei %s Line' % line['name'])
        else:
            embed = Rails.search_line(author_name, author_avatar_url, self._color,
                                      context.option_values.line_name, self.lines, self._short_name,
                                      self._footer_name, 'Toei %s Line')
        await context.respond(embed)
