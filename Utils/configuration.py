import datetime

from marshmallow import Schema, fields, post_load
from typing import List, Optional


class LotteryInfo:
    def __init__(self, lottery_scheduled: datetime.datetime, channel_id: int):
        self.lottery_scheduled = lottery_scheduled
        self.channel_id = channel_id


class LotteryInfoSchema(Schema):
    lottery_scheduled = fields.DateTime()
    channel_id = fields.Int()

    @post_load
    def make_lottery_info(self, data, **kwargs):
        return LotteryInfo(**data)


class Configuration:
    def __init__(self, lottery_info: Optional[LotteryInfo] = None, enabled_channels: Optional[List[int]] = None, ignored_channels: Optional[List[int]] = None):
        if lottery_info is not None:
            self.lottery_info = lottery_info
        if enabled_channels is not None:
            self.enabled_channels = enabled_channels
        if ignored_channels is not None:
            self.ignored_channels = ignored_channels


class ConfigurationSchema(Schema):
    lottery_info = fields.Nested(LotteryInfoSchema)
    enabled_channels = fields.List(fields.Int)
    ignored_channels = fields.List(fields.Int)

    @post_load
    def make_configuration(self, data, **kwargs):
        return Configuration(**data)
