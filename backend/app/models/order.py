from enum import Enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_customer_status", "customer_id", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, name="order_status"), default=OrderStatus.PENDING, index=True)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
