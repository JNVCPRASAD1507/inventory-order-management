from enum import Enum
from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CategoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[CategoryStatus] = mapped_column(SAEnum(CategoryStatus, name="category_status"), default=CategoryStatus.ACTIVE, index=True)

    products = relationship("Product", back_populates="category")
