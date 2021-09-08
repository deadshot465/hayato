import os.path

import yaml

from structures.configuration import Configuration


class ConfigurationService:
    _config_directory_name = 'config'
    _config_file_name = 'config.yaml'
    _config_file_path = os.path.join(os.getcwd(), _config_directory_name, _config_file_name)

    def __init__(self):
        if not os.path.isdir(self._config_directory_name):
            os.mkdir(self._config_directory_name)
        if os.path.exists(self._config_file_path):
            with open(self._config_file_path) as file:
                s = file.read()
                self._config: Configuration = yaml.load(s, Loader=yaml.SafeLoader)
        else:
            self._config = Configuration()
            with open(self._config_file_path, 'w') as file:
                s = yaml.dump(self._config, Dumper=yaml.SafeDumper)
                file.write(s)

    @property
    def prefix(self):
        return self._config.prefix

    @property
    def token(self):
        return self._config.token

    @property
    def log_level(self):
        return self._config.log_level

    @property
    def enabled_channels(self):
        return self._config.enabled_channels

    @property
    def ignored_channels(self):
        return self._config.ignored_channels

    @property
    def trains(self):
        return self._config.trains

    @property
    def responses(self):
        return self._config.responses
