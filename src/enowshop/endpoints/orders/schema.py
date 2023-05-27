import datetime
import enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PaymentMethod(enum.Enum):
    CREDIT_CART = 'credit_card'
    BOLETO = 'boleto'
    PIX = 'pix'
    

class OrderItemsSchema(BaseModel):
    uuid: str
    quantity: int


class CreateOrderSchema(BaseModel):
    address_id: int
    quote_type: str
    payment_method: PaymentMethod = Field(alias="paymentMethod")
    items: List[OrderItemsSchema]

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True 


class   PaymentInfoSchema(BaseModel):

    # pix
    total_value: float
    qrcode: Optional[str]
    qrcode_text: Optional[str]

    expiration_date: Optional[datetime.datetime]


class OrderCreatedSchema(BaseModel):
    uuid: str
    payment_info: PaymentInfoSchema
    channel_uuid: str
    quote_info: Dict


class OrderSchema(BaseModel):
    ...

class ItensSchema(BaseModel):
    uuid: str

class CalcSchema(BaseModel):
    address_uuid: str
    items: List[OrderItemsSchema]

class OrdersPaginateSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[OrderSchema]


class UpdateStatusSchema(BaseModel):
    status: str