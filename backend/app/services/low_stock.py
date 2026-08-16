from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User, UserRole
from app.services.email_service import send_low_stock_email


def queue_low_stock_emails(
    db: Session,
    background_tasks: BackgroundTasks,
    product_id: int,
):
    inventory = db.scalar(
        select(Inventory).where(
            Inventory.product_id == product_id
        )
    )

    if not inventory:
        return

    if inventory.current_stock > inventory.minimum_stock_level:
        return

    product = db.get(Product, product_id)

    if not product:
        return

    users = db.scalars(
        select(User).where(
            User.role.in_(
                [
                    UserRole.ADMIN,
                    UserRole.STAFF,
                ]
            ),
            User.is_active.is_(True),
        )
    ).all()

    for user in users:
        background_tasks.add_task(
            send_low_stock_email,
            email=user.email,
            name=user.full_name,
            product_name=product.name,
            product_id=product.id,
            current_stock=inventory.current_stock,
            minimum_stock_level=inventory.minimum_stock_level,
        )