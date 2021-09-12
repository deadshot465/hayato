import json
import typing

import hikari
from commands.rails.rails import Rails
from lightbulb import slash_commands
from utils.utils import get_author_name


@Rails.subcommand()
class Mtr(slash_commands.SlashSubCommand):
    description: str = 'Randomly get or query information on an MTR Line.'
    enabled_guilds: list[int] = [705036924330704968]
    line_name: typing.Optional[str] = \
        slash_commands.Option('The MTR line name you want to ask about. Type "info" or "list" to see more.')

    path = 'assets/rails/mtr.json'
    thumbnail = 'https://cdn.discordapp.com/attachments/734604988717858846/739961151005130882/MTR.png'
    formal_name = 'MTR'
    short_name = 'MTR'
    footer_name = 'the MTR'
    color = hikari.Color.of(0x9d2133)

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
                                 footer_name=self.footer_name,
                                 thumbnail=self.thumbnail)

    def __get_list_embed(self, author_name: str, author_avatar_url: str, line_list: str) \
            -> hikari.Embed:
        return Rails.build_general_embed(author_name=author_name,
                                         author_avatar_url=author_avatar_url,
                                         title=self.short_name,
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
                                                    self.footer_name, line['name'] + ' Line')
        else:
            embed = Rails.search_line(author_name, author_avatar_url, self.color,
                                      context.option_values.line_name, self.lines, self.short_name,
                                      self.footer_name, '%s Line')
        await context.respond(embed)
