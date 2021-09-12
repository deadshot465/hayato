import datetime

import attr
import yaml


@attr.s(kw_only=True)
class LotteryParticipant(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = u'!LotteryParticipant'

    user_name: str = attr.ib()
    user_id: int = attr.ib()
    lotteries: list[list[int]] = attr.ib(default=[])
    last_daily_time: datetime.datetime = attr.ib(default=datetime.datetime.now())
    last_weekly_time: datetime.datetime = attr.ib(default=datetime.datetime.now())
