from enum import Enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CARD = "card"
    UPI = "upi"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("order_id", name="uq_payment_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod, name="payment_method"))
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus, name="payment_status"), default=PaymentStatus.PENDING, index=True)

    order = relationship("Order", back_populates="payment")
