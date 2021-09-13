import attr
import yaml


@attr.s(kw_only=True)
class Configuration(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = u'!Configuration'

    _default_trains = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5',
                       'Shinkansen E6', 'Shinkansen E7', 'JR East E233', 'JR East E235']
    _default_responses = ['I am a punctual and trustworthy man!',
                          'Hello! My name is Hayasugi Hayato. Nice to meet you!',
                          'Uhh...I am afraid of heights...Don\'t tell me to board an airplane!',
                          'Change form, Shinkalion!',
                          'My dream is to be a Shinkansen train conductor!',
                          'All people who like Shinkansen are good people!',
                          'Shinkansen trains are so cool!',
                          'Shinkansen E5 Series is my favourite!',
                          'Do you know how much it costs for a Shinkansen trip from Tokyo to Osaka?']

    prefix: str = attr.ib(default='h!')
    token: str = attr.ib(default='')
    log_level: str = attr.ib(default='DEBUG')
    enabled_channels: list[int] = attr.ib(default=[])
    ignored_channels: list[int] = attr.ib(default=[])
    trains: list[str] = attr.ib(default=_default_trains)
    responses: list[str] = attr.ib(default=_default_responses)
    google_api_ley: str = attr.ib(default='')
    fetch_from_server: bool = attr.ib(default=False)
    login_name: str = attr.ib(default='')
    login_pass: str = attr.ib(default='')
    rapid_api_key: str = attr.ib(default='')
    mention_reply_chance: int = attr.ib(default=90)
    random_reply_chance: int = attr.ib(default=97)
