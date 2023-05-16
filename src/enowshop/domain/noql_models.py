from datetime import datetime
from typing import List, Optional

from odmantic import Model, Field, EmbeddedModel, Index


class Items(EmbeddedModel):
    product_uuid: str = Field(max_length=36)
    quantity: int = Field(default=1)


class Cars(Model):
    user_uuid: str = Field(unique=True)
    items: List[Items]
    created_at: datetime = Field(default=datetime.now())

    class Config:
        collection = "Cars"

        @staticmethod
        def indexes():
            yield Index(Cars.user_uuid, unique=True)
