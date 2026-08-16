from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product, ProductStatus
from app.models.user import User, UserRole
from app.models.notification import NotificationType

from app.schemas.order import OrderCreate

from app.services.notification import queue_notification

from app.services.email_service import (
    send_order_confirmation_email,
    send_order_status_email,
    send_low_stock_email,
)

VALID_TRANSITIONS = {
    OrderStatus.PENDING: {
        OrderStatus.CONFIRMED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED,
    },
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


def create_order(
    db: Session,
    customer_id: int,
    data: OrderCreate,
    background_tasks,
):
    product_ids = [item.product_id for item in data.items]

    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            400,
            "Duplicate products are not allowed in one order",
        )

    if not data.items:
        raise HTTPException(
            400,
            "Order must contain at least one item",
        )

    # Get customer
    customer = db.get(User, customer_id)

    if not customer:
        raise HTTPException(
            404,
            "Customer not found",
        )

    order = Order(
        customer_id=customer_id,
        total_amount=Decimal("0"),
        status=OrderStatus.PENDING,
    )

    db.add(order)
    db.flush()

    total = Decimal("0")

    low_stock_products = []

    for item in data.items:

        if item.quantity <= 0:
            raise HTTPException(
                400,
                "Quantity must be greater than zero",
            )

        product = db.scalar(
            select(Product).where(Product.id == item.product_id).with_for_update()
        )

        if not product:
            raise HTTPException(
                404,
                f"Product {item.product_id} not found",
            )

        if product.status != ProductStatus.ACTIVE:
            raise HTTPException(
                400,
                f"Product {product.name} is inactive",
            )

        inventory = db.scalar(
            select(Inventory)
            .where(Inventory.product_id == product.id)
            .with_for_update()
        )

        stock = inventory.current_stock if inventory else product.stock_quantity

        if item.quantity > stock:
            raise HTTPException(
                409,
                f"Insufficient stock for {product.name}",
            )

        # Keep stock before changing it
        old_stock = stock

        # Update inventory
        if inventory:
            inventory.current_stock -= item.quantity

        product.stock_quantity = stock - item.quantity

        # Order item
        line_total = product.price * item.quantity

        total += line_total

        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                line_total=line_total,
            )
        )

        # ---------------------------------------
        # LOW STOCK DETECTION
        # ---------------------------------------

        if inventory:
            new_stock = inventory.current_stock
            minimum_stock = inventory.minimum_stock_level

        if old_stock > minimum_stock and new_stock <= minimum_stock:
            low_stock_products.append(
                {
                    "product_name": product.name,
                    "product_id": product.id,
                    "current_stock": new_stock,
                    "minimum_stock_level": minimum_stock,
                }
            )

    order.total_amount = total

    # Commit order and stock changes
    db.commit()
    db.refresh(order)

    # ---------------------------------------
    # IN-APP ORDER NOTIFICATION
    # ---------------------------------------

    queue_notification(
        background_tasks,
        customer_id,
        "Order created",
        f"Order #{order.id} was created successfully.",
        NotificationType.ORDER,
    )

    # ---------------------------------------
    # LOW STOCK EMAIL
    # ---------------------------------------

    if low_stock_products:

        admin_staff = list(
        db.scalars(
            select(User).where(
                User.role.in_(
                    [
                        UserRole.ADMIN,
                        UserRole.STAFF,
                    ]
                ),
                User.is_active.is_(True),
            )
        )
    )

        for product_data in low_stock_products:

            for staff_user in admin_staff:

                background_tasks.add_task(
                send_low_stock_email,
                email=staff_user.email,
                name=staff_user.full_name,
                product_name=product_data["product_name"],
                product_id=product_data["product_id"],
                current_stock=product_data["current_stock"],
                minimum_stock_level=product_data[
                    "minimum_stock_level"
                ],
            )

    return order


def _restore_stock(
    db: Session,
    order: Order,
):
    """
    Restore inventory when an order is cancelled.
    """

    for item in order.items:

        product = db.get(
            Product,
            item.product_id,
        )

        if product:
            product.stock_quantity = (product.stock_quantity or 0) + item.quantity

        inventory = db.scalar(
            select(Inventory).where(Inventory.product_id == item.product_id)
        )

        if inventory:
            inventory.current_stock += item.quantity


def transition_order(
    db: Session,
    order: Order,
    target: OrderStatus,
    background_tasks,
):
    current_status = order.status

    if target not in VALID_TRANSITIONS.get(
        current_status,
        set(),
    ):
        raise HTTPException(
            409,
            f"Invalid transition: " f"{current_status.value} → {target.value}",
        )

    # ---------------------------------------
    # RESTORE STOCK ON CANCEL
    # ---------------------------------------

    if target == OrderStatus.CANCELLED and current_status != OrderStatus.CANCELLED:
        _ = order.items

        _restore_stock(
            db,
            order,
        )

    # ---------------------------------------
    # UPDATE ORDER STATUS
    # ---------------------------------------

    order.status = target

    db.commit()
    db.refresh(order)

    # ---------------------------------------
    # IN-APP NOTIFICATION
    # ---------------------------------------

    queue_notification(
        background_tasks,
        order.customer_id,
        f"Order {target.value}",
        f"Order #{order.id} is now {target.value}.",
        NotificationType.ORDER,
    )

    # ---------------------------------------
    # GET CUSTOMER
    # ---------------------------------------

    customer = db.get(
        User,
        order.customer_id,
    )

    if not customer:
        return order

    # ---------------------------------------
    # ORDER CONFIRMATION EMAIL
    # ---------------------------------------

    if target == OrderStatus.CONFIRMED:

        background_tasks.add_task(
            send_order_confirmation_email,
            email=customer.email,
            name=customer.full_name,
            order_id=order.id,
            order_date=(
                order.order_date.strftime("%Y-%m-%d %H:%M:%S")
                if order.order_date
                else ""
            ),
            payment_status="Pending",
            total_amount=float(order.total_amount),
        )

    # ---------------------------------------
    # ORDER STATUS UPDATE EMAIL
    # ---------------------------------------

    elif target in {
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
    }:

        background_tasks.add_task(
            send_order_status_email,
            email=customer.email,
            name=customer.full_name,
            order_id=order.id,
            old_status=current_status.value,
            new_status=target.value,
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tracking_number=None,
        )

    return order
