from enowshop.endpoints.quotes.schema import QuotesListSchema
from enowshop.helpers import int_to_float
from pydantic import BaseModel, validator
from typing import Dict, List, Optional
from datetime import datetime


class CarItems(BaseModel):
    product_uuid: str


class Item(BaseModel):
    quantity: int
    name: str
    value: int
    image_url: str
    product_uuid: str


class ChangeQuantity(BaseModel):
    quantity: int


class ProductsSchema(BaseModel):
    uuid: str
    name: str
    description: str
    price: float
    unity: int
    image_url: str
    quantity_car: int

    class Config:
        orm_mode = True

    @validator('price')
    def price_to_float(cls, v):
        return int_to_float(v)
    

class CarSchema(BaseModel):
    user_uuid: str
    cart_total: str
    cart_total_term: str
    cash: str
    quoet_value: Optional[str]
    quoets: Optional[List[Dict]]
    items: List[ProductsSchema]
