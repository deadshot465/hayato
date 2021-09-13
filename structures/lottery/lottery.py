import attr
import yaml

from structures.lottery.lottery_info import LotteryInfo
from structures.lottery.lottery_participant import LotteryParticipant


@attr.s(kw_only=True)
class Lottery(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = u'!Lottery'

    lottery_info: LotteryInfo = attr.ib(default=LotteryInfo())
    lottery_participants: list[LotteryParticipant] = attr.ib(default=[])
