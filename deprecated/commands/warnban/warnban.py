from marshmallow import Schema
from marshmallow_dataclass import dataclass
from typing import ClassVar, List, Type
import datetime


@dataclass
class WarnBanData:
    username: str
    user_id: int
    warns: int
    is_banned: bool
    ban_time: datetime.datetime
    ban_expiry: datetime.datetime
    reasons: List[str]
    Schema: ClassVar[Type[Schema]]

    def __init__(self, username: str, user_id: int, warns: int, is_banned: bool, ban_time: datetime.datetime, ban_expiry: datetime.datetime, reasons: List[str]):
        self.username = username
        self.user_id = user_id
        self.warns = warns
        self.is_banned = is_banned
        self.ban_time = ban_time
        self.ban_expiry = ban_expiry
        self.reasons = reasons
