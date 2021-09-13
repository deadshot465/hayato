import datetime

import attr
import yaml


@attr.s(kw_only=True)
class LotteryInfo(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = u'!LotteryInfo'

    channel_id: int = attr.ib(default=737025196237520996)
    lottery_scheduled: datetime.datetime = attr.ib(default=datetime.datetime.now())
