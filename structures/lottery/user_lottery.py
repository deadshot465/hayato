import marshmallow
from marshmallow_dataclass import dataclass
from typing import ClassVar, List, Type


@dataclass
class UserLottery:
    id: str
    user_id: str
    next_daily_time: str
    next_weekly_time: str
    lotteries: List[List[int]]
    Schema: ClassVar[Type[marshmallow.Schema]]
