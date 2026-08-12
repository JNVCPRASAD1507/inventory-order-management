from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: PaymentMethod
    payment_date: datetime
    status: PaymentStatus
    model_config = {"from_attributes": True}
