import json
import typing

import hikari
from commands.rails.rails import Rails
from lightbulb import slash_commands
from utils.utils import get_author_name


@Rails.subcommand()
class TokyoMetro(slash_commands.SlashSubCommand):
    description: str = 'Randomly get or query information on a Tokyo Metro line.'
    line_name: typing.Optional[str] = \
        slash_commands.Option('The Tokyo Metro line name you want to ask about. Type "info" or "list" to see more.')

    path = 'assets/rails/tokyo_metro.json'
    thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/739284406556033034/Tokyo_Metro.png'
    formal_name = 'Tokyo Metro'
    short_name = 'Tokyo Metro'
    footer_name = 'the Tokyo Metro'
    color = hikari.Color.of(0x149dd3)

    def __init__(self, bot):
        super().__init__(bot)
        with open(self.path, 'r', encoding='utf-8') as file:
            self.lines: list[dict] = json.loads(file.read())

    def __get_info_embed(self, author_name: str, author_avatar_url: str) -> hikari.Embed:
        return Rails \
            .build_general_embed(author_name=author_name,
                                 author_avatar_url=author_avatar_url,
                                 title=self.formal_name,
                                 color=self.color,
                                 description='The Tokyo Metro is a major rapid transit system in Tokyo, Japan. While it'
                                             ' is not the only rapid transit system operating in Tokyo, it has the '
                                             'higher ridership among the two subway operators: in 2014, the Tokyo Metro'
                                             ' had an average daily ridership of 6.84 million passengers, with 9 lines'
                                             ' and 180 stations.\n\n Tokyo Metro is operated by Tokyo Metro Co., Ltd.,'
                                             ' a private company jointly owned by the Japanese government (through the'
                                             ' Ministry of Finance) and the Tokyo metropolitan government.',
                                 footer_name=self.footer_name,
                                 thumbnail=self.thumbnail)

    def __get_list_embed(self, author_name: str, author_avatar_url: str, line_list: str) \
            -> hikari.Embed:
        return Rails.build_general_embed(author_name=author_name,
                                         author_avatar_url=author_avatar_url,
                                         title='Tokyo Metro',
                                         color=self.color,
                                         description='Here is a list of lines in the %s:\n\n%s' %
                                                     (self.short_name, line_list),
                                         footer_name=self.footer_name,
                                         thumbnail=self.thumbnail)

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
                                                    self.footer_name, 'Tokyo Metro %s Line' % line['name'])
        else:
            embed = Rails.search_line(author_name, author_avatar_url, self.color,
                                      context.option_values.line_name, self.lines, self.short_name,
                                      self.footer_name, 'Tokyo Metro %s Line')
        await context.respond(embed)
