import datetime
import json
import marshmallow_dataclass

from deprecated.commands.lottery.lottery import LotteryParticipant
from typing import List
from utils.deprecated.configuration import Configuration, ConfigurationSchema


class ConfigurationManager(object):
    participant_schema = marshmallow_dataclass.class_schema(LotteryParticipant)
    config_path = 'assets/config.json'
    lottery_path = 'assets/lottery.json'
    configuration_schema = ConfigurationSchema()
    with open(config_path) as file_1:
        config: Configuration = configuration_schema.loads(json_data=file_1.read())
    with open(lottery_path) as file_1:
        lottery_data: List[LotteryParticipant] = participant_schema().loads(json_data=file_1.read(), many=True)

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

    @classmethod
    def get_next_lottery_time(cls) -> datetime.datetime:
        return cls.config.lottery_info.lottery_scheduled

    @classmethod
    def set_next_lottery_time(cls):
        if datetime.datetime.today().weekday() == 3:
            cls.config.lottery_info.lottery_scheduled += datetime.timedelta(days=3)
        elif datetime.datetime.today().weekday() == 6:
            cls.config.lottery_info.lottery_scheduled += datetime.timedelta(days=4)
        print("Next lottery date: ", cls.config.lottery_info.lottery_scheduled)
        serialized = cls.configuration_schema.dumps(cls.config)
        print("Serialized: ", serialized)
        with open(cls.config_path, 'w') as file_1:
            obj = dict(json.loads(serialized))
            file_1.write(json.dumps(obj, indent=2))

    @classmethod
    def write_lottery_data(cls):
        serialized = cls.participant_schema().dumps(cls.lottery_data, many=True)
        with open(cls.lottery_path, 'w') as file_1:
            obj = json.loads(serialized)
            file_1.write(json.dumps(obj, indent=2))

    @classmethod
    def reload_lottery_data(cls):
        with open(cls.lottery_path) as file_1:
            cls.lottery_data = cls.participant_schema().loads(json_data=file_1.read(), many=True)
