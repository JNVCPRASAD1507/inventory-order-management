from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.product import Product
from app.models.user import User, UserRole

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def counts(db: Session):
    total_orders = (
        db.scalar(
            select(func.count(Order.id))
        )
        or 0
    )

    pending = (
        db.scalar(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.PENDING)
        )
        or 0
    )

    completed = (
        db.scalar(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.DELIVERED)
        )
        or 0
    )

    cancelled = (
        db.scalar(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.CANCELLED)
        )
        or 0
    )

    low = (
        db.scalar(
            select(func.count(Inventory.id))
            .where(
                Inventory.current_stock
                <= Inventory.minimum_stock_level
            )
        )
        or 0
    )

    # Revenue = successfully paid payments
    revenue = (
        db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.status == PaymentStatus.PAID)
        )
        or 0
    )

    return {
        "total_customers": (
            db.scalar(
                select(func.count(User.id))
                .where(User.role == UserRole.CUSTOMER)
            )
            or 0
        ),
        "total_staff": (
            db.scalar(
                select(func.count(User.id))
                .where(User.role == UserRole.STAFF)
            )
            or 0
        ),
        "total_products": (
            db.scalar(
                select(func.count(Product.id))
            )
            or 0
        ),
        "total_categories": (
            db.scalar(
                select(func.count(Category.id))
            )
            or 0
        ),
        "total_orders": total_orders,
        "pending_orders": pending,
        "completed_orders": completed,
        "cancelled_orders": cancelled,
        "low_stock_products": low,
        "total_revenue": float(revenue),
    }


def series(db: Session, days: int):
    since = datetime.now(timezone.utc) - timedelta(days=days - 1)

    rows = db.execute(
        select(
            func.date(Order.order_date),
            func.count(Order.id),
            func.coalesce(func.sum(Payment.amount), 0),
        )
        .join(
            Payment,
            Payment.order_id == Order.id,
        )
        .where(
            Order.order_date >= since,
            Payment.status == PaymentStatus.PAID,
        )
        .group_by(
            func.date(Order.order_date)
        )
        .order_by(
            func.date(Order.order_date)
        )
    ).all()

    return [
        {
            "date": str(date),
            "orders": int(order_count),
            "revenue": float(revenue),
        }
        for date, order_count, revenue in rows
    ]


@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN)),
):
    return {
        "metrics": counts(db),
        "daily": series(db, 14),
        "weekly": series(db, 56),
        "monthly": series(db, 180),
    }


@router.get("/staff")
def staff_dashboard(
    db: Session = Depends(get_db),
    _=Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.STAFF,
        )
    ),
):
    today = datetime.now(timezone.utc).date()

    todays = (
        db.scalar(
            select(func.count(Order.id))
            .where(
                func.date(Order.order_date) == today
            )
        )
        or 0
    )

    low = (
        db.scalar(
            select(func.count(Inventory.id))
            .where(
                Inventory.current_stock
                <= Inventory.minimum_stock_level
            )
        )
        or 0
    )

    # Staff revenue = successfully paid payments
    revenue = (
        db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.status == PaymentStatus.PAID)
        )
        or 0
    )

    return {
        "total_products": (
            db.scalar(
                select(func.count(Product.id))
            )
            or 0
        ),

        "low_stock_products": low,

        "todays_orders": todays,

        "pending_orders": (
            db.scalar(
                select(func.count(Order.id))
                .where(
                    Order.status == OrderStatus.PENDING
                )
            )
            or 0
        ),

        "completed_orders": (
            db.scalar(
                select(func.count(Order.id))
                .where(
                    Order.status == OrderStatus.DELIVERED
                )
            )
            or 0
        ),

        "total_revenue": float(revenue),

        "daily": series(db, 14),
        "weekly": series(db, 56),
        "monthly": series(db, 180),
    }


@router.get("/customer")
def customer_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(UserRole.CUSTOMER)
    ),
):
    base = select(func.count(Order.id)).where(
        Order.customer_id == user.id
    )

    total = db.scalar(base) or 0

    pending = (
        db.scalar(
            base.where(
                Order.status == OrderStatus.PENDING
            )
        )
        or 0
    )

    completed = (
        db.scalar(
            base.where(
                Order.status == OrderStatus.DELIVERED
            )
        )
        or 0
    )

    cancelled = (
        db.scalar(
            base.where(
                Order.status == OrderStatus.CANCELLED
            )
        )
        or 0
    )

    # Customer amount spent = successfully paid payments
    spent = (
        db.scalar(
            select(
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                )
            )
            .join(
                Order,
                Payment.order_id == Order.id,
            )
            .where(
                Order.customer_id == user.id,
                Payment.status == PaymentStatus.PAID,
            )
        )
        or 0
    )

    return {
        "total_orders": total,
        "pending_orders": pending,
        "completed_orders": completed,
        "cancelled_orders": cancelled,
        "total_amount_spent": float(spent),
    }