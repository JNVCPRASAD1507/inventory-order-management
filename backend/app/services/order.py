from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product, ProductStatus
from app.models.notification import NotificationType
from app.schemas.order import OrderCreate
from app.services.notification import queue_notification

VALID_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


def create_order(db: Session, customer_id: int, data: OrderCreate, background_tasks):
    product_ids = [item.product_id for item in data.items]
    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(400, "Duplicate products are not allowed in one order")
    if not data.items:
        raise HTTPException(400, "Order must contain at least one item")

    order = Order(customer_id=customer_id, total_amount=Decimal("0"), status=OrderStatus.PENDING)
    db.add(order)
    db.flush()

    total = Decimal("0")
    for item in data.items:
        if item.quantity <= 0:
            raise HTTPException(400, "Quantity must be greater than zero")

        product = db.scalar(
            select(Product).where(Product.id == item.product_id).with_for_update()
        )
        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")
        if product.status != ProductStatus.ACTIVE:
            raise HTTPException(400, f"Product {product.name} is inactive")

        inventory = db.scalar(
            select(Inventory).where(Inventory.product_id == product.id).with_for_update()
        )
        stock = inventory.current_stock if inventory else product.stock_quantity
        if item.quantity > stock:
            raise HTTPException(409, f"Insufficient stock for {product.name}")

        if inventory:
            inventory.current_stock -= item.quantity
        product.stock_quantity = stock - item.quantity

        line_total = product.price * item.quantity
        total += line_total
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
            line_total=line_total,
        ))

        if inventory and inventory.current_stock <= inventory.minimum_stock_level:
            queue_notification(
                background_tasks,
                customer_id,
                "Low stock alert",
                f"{product.name} has reached its low-stock threshold.",
                NotificationType.STOCK,
            )

    order.total_amount = total
    db.commit()
    db.refresh(order)

    queue_notification(
        background_tasks,
        customer_id,
        "Order created",
        f"Order #{order.id} was created successfully.",
        NotificationType.ORDER,
    )
    return order


def _restore_stock(db: Session, order: Order):
    """Restore inventory when an order is cancelled."""
    for item in order.items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock_quantity = (product.stock_quantity or 0) + item.quantity
        inventory = db.scalar(select(Inventory).where(Inventory.product_id == item.product_id))
        if inventory:
            inventory.current_stock += item.quantity


def transition_order(db: Session, order: Order, target: OrderStatus, background_tasks):
    if target not in VALID_TRANSITIONS.get(order.status, set()):
        raise HTTPException(409, f"Invalid transition: {order.status.value} → {target.value}")

    # Restore stock on cancel (only if not already cancelled)
    if target == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        # Ensure items are loaded
        _ = order.items
        _restore_stock(db, order)

    order.status = target
    db.commit()
    db.refresh(order)
    queue_notification(
        background_tasks,
        order.customer_id,
        f"Order {target.value}",
        f"Order #{order.id} is now {target.value}.",
        NotificationType.ORDER,
    )
    return order
