from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.review import Review
from app.schemas.review import ReviewCreate


def create_review(db: Session, customer_id: int, data: ReviewCreate):
    order = db.scalar(select(Order).where(Order.id == data.order_id, Order.customer_id == customer_id))
    if not order or order.status != OrderStatus.DELIVERED:
        raise HTTPException(403, "Only delivered orders can be reviewed")

    purchased = db.scalar(select(OrderItem).where(
        OrderItem.order_id == data.order_id,
        OrderItem.product_id == data.product_id,
    ))
    if not purchased:
        raise HTTPException(403, "The product was not part of the selected order")

    duplicate = db.scalar(select(Review).where(
        Review.customer_id == customer_id,
        Review.product_id == data.product_id,
        Review.order_id == data.order_id,
    ))
    if duplicate:
        raise HTTPException(409, "You already reviewed this product for this order")

    review = Review(customer_id=customer_id, **data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def average_rating(db: Session, product_id: int):
    result = db.scalar(select(func.avg(Review.rating)).where(Review.product_id == product_id))
    return round(float(result), 2) if result is not None else 0.0
