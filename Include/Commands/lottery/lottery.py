from marshmallow import Schema
from marshmallow_dataclass import dataclass
from typing import ClassVar, List, Type
import datetime


@dataclass
class LotteryParticipant:
    username: str
    user_id: int
    lottery_choices: List[List[int]]
    last_daily_time: datetime.datetime
    last_weekly_time: datetime.datetime
    Schema: ClassVar[Type[Schema]]

    def __init__(self, username: str, user_id: int, lottery_choices: List[List[int]], last_daily_time: datetime.datetime, last_weekly_time: datetime.datetime):
        self.username = username
        self.user_id = user_id
        self.lottery_choices = lottery_choices
        self.last_daily_time = last_daily_time
        self.last_weekly_time = last_weekly_time
