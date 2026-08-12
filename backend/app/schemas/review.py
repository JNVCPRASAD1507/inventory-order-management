from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    product_id: int
    order_id: int
    rating: int = Field(ge=1, le=5)
    review: str = Field(min_length=1, max_length=2000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    review: str | None = Field(default=None, min_length=1, max_length=2000)


class ReviewResponse(ReviewCreate):
    id: int
    customer_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
