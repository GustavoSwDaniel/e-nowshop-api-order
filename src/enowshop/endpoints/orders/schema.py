import datetime
import enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PaymentMethod(enum.Enum):
    CREDIT_CART = 'credit card'
    INVOICE = 'invoice'
    PIX = 'PIX'

class CreditCard(enum.Enum):
    APPROVED = 'approved'
    PENDING = 'pending'
    DENIED = 'denied'
    

class OrderItemsSchema(BaseModel):
    uuid: str
    value: float
    quantity: int


class CreateOrderSchema(BaseModel):
    total_amount: int = Field(alias="totalAmount")
    payment_type: PaymentMethod = Field(alias="paymentMethod")
    instalments: int
    items: List[OrderItemsSchema]

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True 


class PaymentInfoSchema(BaseModel):

    # pix
    total_value: float
    qrcode: Optional[str]
    qrcode_text: Optional[str]

    expiration_date: Optional[datetime.datetime]


class OrderCreatedSchema(BaseModel):
    uuid: str
    payment_info: PaymentInfoSchema


class OrderSchema(BaseModel):
    ...


class OrdersPaginateSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[OrderSchema]