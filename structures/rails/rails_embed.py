from typing import Union

import attr
import hikari


@attr.s(kw_only=True)
class RailsEmbed:
    author_name: str = attr.ib()
    author_avatar_url: str = attr.ib()
    title: str = attr.ib()
    colour: hikari.Color = attr.ib()
    overview: str = attr.ib()
    route: str = attr.ib(default='')
    stations: int = attr.ib(default=0)
    length: float = attr.ib(default=0.0)
    gauge: float = attr.ib(default=0.0)
    formation: str = attr.ib(default='')
    opened: str = attr.ib(default='')
    running_time: str = attr.ib(default='')
    rolling_stock: str = attr.ib(default='')
    maximum_speed: str = attr.ib(default='')
    daily_ridership: str = attr.ib(default='')
    operator: str = attr.ib(default='')
    image: str = attr.ib(default='')
    logo: str = attr.ib(default='')
    footer_name: str = attr.ib(default='')
    constructed: str = attr.ib(default='')
    capacity: str = attr.ib(default='')
    acceleration: str = attr.ib(default='')
    lines_served: str = attr.ib(default='')

    def __setitem__(self, key: str, value):
        setattr(self, key, value)

    @staticmethod
    def __add_field(embed: hikari.Embed, field_name: str, value: Union[int, float, str], inline: bool) \
            -> hikari.Embed:
        if (isinstance(value, int) and value > 0) or \
                (isinstance(value, float) and value > 0.0) or \
                (isinstance(value, str) and len(value) > 0):
            return embed.add_field(name=field_name, value=str(value), inline=inline)
        else:
            return embed

    def build_embed(self) -> hikari.Embed:
        embed = hikari.Embed(title=self.title, color=self.colour, description=self.overview)
        embed.set_author(name=self.author_name,
                         icon=self.author_avatar_url)

        self.__add_field(embed, 'Route', self.route, False)
        self.__add_field(embed, 'Stations', self.stations, True)
        self.__add_field(embed, 'Maximum Speed', self.maximum_speed, True)
        self.__add_field(embed, 'Length (km)', self.length, True)
        self.__add_field(embed, 'Track Gauge (mm)', self.gauge, True)
        self.__add_field(embed, 'Formation', self.formation, True)
        self.__add_field(embed, 'Running Time (minutes)', self.running_time, True)
        self.__add_field(embed, 'Opened', self.opened, True)
        self.__add_field(embed, 'Daily Ridership', self.daily_ridership, True)
        self.__add_field(embed, 'Rolling Stock', self.rolling_stock, False)
        self.__add_field(embed, 'Operator', self.operator, False)
        self.__add_field(embed, 'Constructed', self.constructed, True)
        self.__add_field(embed, 'Acceleration', self.acceleration, True)
        self.__add_field(embed, 'Capacity', self.capacity, False)
        self.__add_field(embed, 'Lines Served', self.lines_served, False)

        if len(self.logo) > 0:
            embed.set_thumbnail(self.logo)
        if len(self.image) > 0:
            embed.set_image(self.image)

        embed.set_footer(text=f'Ride {self.footer_name}!')
        return embed
