from pydantic import BaseModel, Field
from app.models.category import CategoryStatus


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    status: CategoryStatus = CategoryStatus.ACTIVE


class CategoryUpdate(CategoryCreate):
    pass


class CategoryResponse(CategoryCreate):
    id: int
    model_config = {"from_attributes": True}
