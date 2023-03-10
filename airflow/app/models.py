from enum import Enum

from pydantic import BaseModel


class SearchStatusEnum(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class SearchModel(BaseModel):
    search_id: str
    status: SearchStatusEnum
    items: list = []

    class Config:
        use_enum_values = True
