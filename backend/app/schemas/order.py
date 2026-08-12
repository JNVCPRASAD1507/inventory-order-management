from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: Decimal
    status: OrderStatus
    order_date: datetime
    items: list[OrderItemResponse]
    model_config = {"from_attributes": True}
