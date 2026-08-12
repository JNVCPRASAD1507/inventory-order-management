from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.product import ProductStatus


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str | None = None
    category_id: int
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    sku: str = Field(min_length=2, max_length=80)
    stock_quantity: int = Field(default=0, ge=0)
    status: ProductStatus = ProductStatus.ACTIVE


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = None
    category_id: int | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    sku: str | None = Field(default=None, min_length=2, max_length=80)
    status: ProductStatus | None = None


class ProductResponse(ProductCreate):
    id: int
    image_path: str | None = None
    model_config = {"from_attributes": True}
