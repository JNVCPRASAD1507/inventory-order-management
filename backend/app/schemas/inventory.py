from datetime import datetime
from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: int
    current_stock: int = Field(ge=0)
    minimum_stock_level: int = Field(ge=0)
    maximum_stock_level: int = Field(gt=0)


class InventoryUpdate(BaseModel):
    minimum_stock_level: int | None = Field(default=None, ge=0)
    maximum_stock_level: int | None = Field(default=None, gt=0)
    current_stock: int | None = Field(default=None, ge=0)


class StockChange(BaseModel):
    quantity: int = Field(gt=0)


class InventoryResponse(InventoryCreate):
    id: int
    last_updated: datetime
    product_name: str | None = None
    model_config = {"from_attributes": True}
