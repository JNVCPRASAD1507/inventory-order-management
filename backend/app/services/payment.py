from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment, PaymentStatus
from app.models.notification import NotificationType
from app.services.notification import queue_notification


def create_payment(db: Session, customer_id: int, order_id: int, method, background_tasks):
    order = db.get(Order, order_id)
    if not order or order.customer_id != customer_id:
        raise HTTPException(404, "Order not found")
    existing = db.scalar(select(Payment).where(Payment.order_id == order_id))
    if existing:
        raise HTTPException(409, "Payment already exists for this order")

    payment = Payment(order_id=order.id, amount=order.total_amount, payment_method=method, status=PaymentStatus.PAID)
    db.add(payment)
    db.commit()
    db.refresh(payment)

    queue_notification(
        background_tasks,
        customer_id,
        "Payment completed",
        f"Payment for order #{order.id} was completed.",
        NotificationType.PAYMENT,
    )
    return payment


def refund_payment(db: Session, payment: Payment):
    if payment.status == PaymentStatus.REFUNDED:
        raise HTTPException(409, "Payment has already been refunded")
    if payment.status != PaymentStatus.PAID:
        raise HTTPException(409, "Only paid payments can be refunded")
    payment.status = PaymentStatus.REFUNDED
    db.commit()
    db.refresh(payment)
    return payment
