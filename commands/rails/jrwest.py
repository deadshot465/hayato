import json
import typing

import hikari
from commands.rails.rails import Rails
from lightbulb import slash_commands
from utils.utils import get_author_name


@Rails.subcommand()
class JrWest(slash_commands.SlashSubCommand):
    description: str = 'Randomly get or query information on JR West Line.'
    line_name: typing.Optional[str] = \
        slash_commands.Option('The JR West line name you want to ask about. Type "info" or "list" to see more.')

    path = 'assets/rails/jrwest.json'
    thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/741817325732233268/JR_West.png'
    formal_name = 'West Japan Railway Company'
    short_name = 'JR West'
    footer_name = 'JR West'
    color = hikari.Color.of(0x0473bd)

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
                                 description='West Japan Railway Company (西日本旅客鉄道株式会社, Nishi-Nihon Ryokaku Tetsudō '
                                             'Kabushiki-gaisha), also referred to as JR-West '
                                             '(JR西日本, Jeiāru Nishi-Nihon), is one of the Japan Railways Group'
                                             ' (JR Group) companies and operates in western '
                                             'Honshu. It has its headquarters in Kita-ku, Osaka.',
                                 footer_name=self.footer_name,
                                 thumbnail=self.thumbnail)

    def __get_list_embed(self, author_name: str, author_avatar_url: str, line_list: str) \
            -> hikari.Embed:
        return Rails.build_general_embed(author_name=author_name,
                                         author_avatar_url=author_avatar_url,
                                         title=self.short_name,
                                         color=self.color,
                                         description='Here is a list of lines in %s:\n\n%s' %
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
                                                    self.footer_name, line['name'] + ' Line')
        else:
            embed = Rails.search_line(author_name, author_avatar_url, self.color,
                                      context.option_values.line_name, self.lines, self.short_name,
                                      self.footer_name, '%s Line')
        await context.respond(embed)
