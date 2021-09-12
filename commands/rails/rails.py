import random
import typing

import hikari
from lightbulb import slash_commands
from similarity.damerau import Damerau
from structures.rails.rails_embed import RailsEmbed


class Rails(slash_commands.SlashCommandGroup):
    description: str = 'Ask Hayato for information on trains and rails.'
    enabled_guilds: list[int] = [705036924330704968]

    @staticmethod
    def get_random_line(lines: list[dict]) -> dict:
        return random.choice(lines)

    @staticmethod
    def build_general_embed(*, author_name: str,
                            author_avatar_url: str,
                            title: str, color: hikari.Color, description: str, footer_name: str, thumbnail: str = '') \
            -> hikari.Embed:
        return RailsEmbed(author_name=author_name,
                          author_avatar_url=author_avatar_url,
                          title=title,
                          colour=color,
                          overview=description,
                          footer_name=footer_name,
                          logo=thumbnail).build_embed()

    @staticmethod
    def build_single_result_embed(author_name: str,
                                  author_avatar_url: str,
                                  line: dict,
                                  footer_name: str,
                                  title: str) -> hikari.Embed:
        embed = RailsEmbed(author_name=author_name,
                           author_avatar_url=author_avatar_url,
                           title=title,
                           colour=hikari.Color.of(line['colour']), footer_name=footer_name,
                           overview=line['overview'])
        for (k, v) in line.items():
            embed[k] = v
        return embed.build_embed()

    @staticmethod
    def search_line(author_name: str,
                    author_avatar_url: str,
                    color: hikari.Color,
                    keyword: str, lines: list[dict],
                    railway_name: str,
                    footer_name: str, name_format: str, *, keyword_limit=3) -> typing.Union[str, hikari.Embed]:
        if len(keyword) < keyword_limit:
            return f'The keyword has to be at least {keyword_limit} characters long!'

        lowercase_keyword = keyword.lower()

        def filter_lines(item: dict) -> bool:
            abbrev: typing.Optional[str] = item.get('abbrev')
            if abbrev is None:
                lowercase_abbrev = ''
            else:
                lowercase_abbrev = abbrev.lower()
            lowercase_name = item['name'].lower()
            if (lowercase_keyword == lowercase_abbrev) or \
                    (lowercase_keyword == lowercase_name) or \
                    (lowercase_keyword in lowercase_name):
                return True
            return False

        found_lines = list(filter(filter_lines, lines))
        if len(found_lines) > 1:
            return Rails.__build_multiple_result_embed(author_name, author_avatar_url, color, found_lines)
        elif len(found_lines) == 0:
            return Rails.__fuzzy_search(author_name, author_avatar_url, color, keyword, lines, railway_name)
        else:
            line = found_lines.pop()
            return Rails.build_single_result_embed(author_name, author_avatar_url, line,
                                                   footer_name, name_format % line['name'])

    @staticmethod
    def __build_multiple_result_embed(author_name: str,
                                      author_avatar_url: str,
                                      color: hikari.Color,
                                      found_lines: list[dict]) -> hikari.Embed:
        embed = hikari.Embed(title='Search Result',
                             description='The following are possible search results.',
                             color=color)
        embed.set_author(name=author_name, icon=author_avatar_url)
        line_names = list(map(lambda l: '`{}`'.format(l['name']), found_lines))
        return embed.add_field(name='Results', value='\n'.join(line_names), inline=False)

    @staticmethod
    def __fuzzy_search(author_name: str, author_avatar_url: str,
                       color: hikari.Color, query: str, lines: list[dict], railway_name: str) \
            -> typing.Union[str, hikari.Embed]:
        line_names = list(map(lambda l: l['name'], lines))
        damerau = Damerau()

        def check_distance(name: str) -> bool:
            distance = damerau.distance(query, name)
            return distance <= 4.0

        filtered_line_names = list(filter(check_distance, line_names))
        if len(filtered_line_names) == 0:
            return f'There is no such line in {railway_name}!'
        else:
            embed = hikari.Embed(title='Search Result',
                                 description='Sorry, I cannot find any results. Did you mean...',
                                 color=color)
            embed.set_author(name=author_name, icon=author_avatar_url)
            joined_lines_names = '\n'.join(list(map(lambda l: '`{}`'.format(l), filtered_line_names)))
            return embed.add_field(name='Results', value=joined_lines_names, inline=False)
