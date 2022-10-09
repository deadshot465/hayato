import os.path
import typing

import lightbulb
import yaml

from structures.configuration import Configuration


class ConfigurationService:
    _config_directory_name = 'config'
    _config_file_name = 'config.yaml'
    _config_file_path = os.path.join(os.getcwd(), _config_directory_name, _config_file_name)

    def __init__(self):
        self._bot: typing.Optional[lightbulb.BotApp] = None
        if not os.path.isdir(self._config_directory_name):
            os.mkdir(self._config_directory_name)
        if os.path.exists(self._config_file_path):
            with open(self._config_file_path) as file:
                s = file.read()
                self._config: Configuration = yaml.load(s, Loader=yaml.SafeLoader)
        else:
            self._config = Configuration()
            self.__write_config()

    def allow_channel(self, channel_id: int):
        self._config.ignored_channels = [channel for channel in self._config.ignored_channels if channel != channel_id]
        self.__write_config()

    def ignore_channel(self, channel_id: int):
        self._config.ignored_channels.append(channel_id)
        self._config.ignored_channels = list(set(self._config.ignored_channels))
        self.__write_config()

    def __write_config(self):
        with open(self._config_file_path, 'w') as file:
            s = yaml.dump(self._config, Dumper=yaml.SafeDumper)
            file.write(s)

    @property
    def prefix(self) -> str:
        return self._config.prefix

    @property
    def token(self) -> str:
        return self._config.token

    @property
    def log_level(self) -> str:
        return self._config.log_level

    @property
    def enabled_channels(self) -> list[int]:
        return self._config.enabled_channels

    @property
    def ignored_channels(self) -> list[int]:
        return self._config.ignored_channels

    @property
    def trains(self) -> list[str]:
        return self._config.trains

    @property
    def responses(self) -> list[str]:
        return self._config.responses

    @property
    def fetch_from_server(self) -> bool:
        return self._config.fetch_from_server

    @property
    def login_name(self) -> str:
        return self._config.login_name

    @property
    def login_pass(self) -> str:
        return self._config.login_pass

    @property
    def mention_reply_chance(self) -> int:
        return self._config.mention_reply_chance

    @property
    def random_reply_chance(self) -> int:
        return self._config.random_reply_chance

    @property
    def rapid_api_key(self) -> str:
        return self._config.rapid_api_key

    @property
    def joat_endpoint(self) -> str:
        return self._config.joat_endpoint

    @property
    def api_endpoint(self) -> str:
        return self._config.api_endpoint

    @property
    def upload_destination(self) -> str:
        return self._config.upload_destination

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, value: lightbulb.BotApp):
        self._bot = value


configuration_service = ConfigurationService()
