import marshmallow
from marshmallow_dataclass import dataclass
from typing import ClassVar, Type


@dataclass
class UserCredit:
    id: str
    username: str
    user_id: str
    credits: int
    Schema: ClassVar[Type[marshmallow.Schema]]
