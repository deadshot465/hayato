import json
import marshmallow_dataclass

from Include.Commands.lottery.lottery import LotteryParticipant
from typing import List
from Utils.configuration import Configuration, ConfigurationSchema


class ConfigurationManager(object):
    participant_schema = marshmallow_dataclass.class_schema(LotteryParticipant)
    config_path = 'Storage/config.json'
    configuration_schema = ConfigurationSchema()
    with open(config_path) as file_1:
        config: Configuration = configuration_schema.loads(json_data=file_1.read())

    @classmethod
    def update_channel(cls, action: str, channel_id: int) -> bool:
        if action == 'enable':
            cls.config.enabled_channels.append(channel_id)
        elif action == 'disable':
            cls.config.enabled_channels.remove(channel_id)
        elif action == 'allow':
            cls.config.ignored_channels.remove(channel_id)
        elif action == 'ignore':
            cls.config.ignored_channels.append(channel_id)
        serialized = cls.configuration_schema.dumps(cls.config)
        with open(cls.config_path, 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))
        return True

    @classmethod
    def get_available_channels(cls) -> List[int]:
        return cls.config.enabled_channels

    @classmethod
    def get_ignored_channels(cls) -> List[int]:
        return cls.config.ignored_channels
