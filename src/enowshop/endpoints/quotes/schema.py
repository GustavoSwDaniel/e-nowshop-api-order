from pydantic import BaseModel, Field
from typing import List, Dict


class QuotesListSchema(BaseModel):
    quotes: List[Dict]

class ProductSchema(BaseModel):
    uuid: str
    quantity: int

class ProductsListSchema(BaseModel):
    products: List[Dict]