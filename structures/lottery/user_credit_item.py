import marshmallow
from marshmallow_dataclass import dataclass
from typing import ClassVar, Type


@dataclass
class UserCreditItem:
    Id: int
    Username: str
    UserId: str
    Credits: int
    Schema: ClassVar[Type[marshmallow.Schema]]
