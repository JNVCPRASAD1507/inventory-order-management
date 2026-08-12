from enum import Enum
from decimal import Decimal
from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_price_status", "price", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    sku: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ProductStatus] = mapped_column(SAEnum(ProductStatus, name="product_status"), default=ProductStatus.ACTIVE, index=True)
    image_path: Mapped[str | None] = mapped_column(String(500))

    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
