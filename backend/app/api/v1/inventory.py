from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import UserRole
from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    StockChange,
)
from app.services.low_stock import queue_low_stock_emails

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=201,
)
def create_inventory(
    data: InventoryCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    if not db.get(Product, data.product_id):
        raise HTTPException(404, "Product not found")

    if db.scalar(select(Inventory).where(Inventory.product_id == data.product_id)):
        raise HTTPException(
            409,
            "Inventory already exists",
        )

    if data.current_stock > data.maximum_stock_level:
        raise HTTPException(
            400,
            "Current stock cannot exceed maximum stock",
        )

    item = Inventory(**data.model_dump())

    product = db.get(Product, data.product_id)
    product.stock_quantity = data.current_stock

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get(
    "",
    response_model=list[InventoryResponse],
)
def list_inventory(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    rows = list(db.scalars(select(Inventory).order_by(Inventory.id.desc())))

    out = []

    for item in rows:
        data = InventoryResponse.model_validate(item)

        product = db.get(Product, item.product_id)

        data.product_name = product.name if product else None

        out.append(data)

    return out


@router.get(
    "/low-stock",
    response_model=list[InventoryResponse],
)
def low_stock(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    return list(
        db.scalars(
            select(Inventory).where(
                Inventory.current_stock <= Inventory.minimum_stock_level
            )
        )
    )


@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
)
def get_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    item = db.scalar(select(Inventory).where(Inventory.product_id == product_id))

    if not item:
        raise HTTPException(
            404,
            "Inventory not found",
        )

    return item


@router.put(
    "/{product_id}",
    response_model=InventoryResponse,
)
def update_inventory(
    product_id: int,
    data: InventoryUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    item = db.scalar(
        select(Inventory).where(Inventory.product_id == product_id).with_for_update()
    )

    if not item:
        raise HTTPException(
            404,
            "Inventory not found",
        )

    payload = data.model_dump(exclude_unset=True)

    if (
        "maximum_stock_level" in payload
        and item.current_stock > payload["maximum_stock_level"]
    ):
        raise HTTPException(
            400,
            "Maximum stock cannot be below current stock",
        )

    for k, v in payload.items():
        setattr(item, k, v)

    if "current_stock" in payload:
        db.get(
            Product,
            product_id,
        ).stock_quantity = payload["current_stock"]

    db.commit()
    db.refresh(item)

    queue_low_stock_emails(
        db,
        background_tasks,
        product_id,
    )

    return item


def _change(
    product_id: int,
    qty: int,
    add: bool,
    db: Session,
    background_tasks: BackgroundTasks,
):
    item = db.scalar(
        select(Inventory).where(Inventory.product_id == product_id).with_for_update()
    )

    if not item:
        raise HTTPException(
            404,
            "Inventory not found",
        )
        
        # Calculate new stock

    new_stock = item.current_stock + qty if add else item.current_stock - qty
        # Prevent negative stock
    if new_stock < 0:
        raise HTTPException(
            409,
            "Stock cannot become negative",
        )
    # Prevent exceeding maximum stock
    if new_stock > item.maximum_stock_level:
        raise HTTPException(
            409,
            "Stock exceeds maximum stock level",
        )
     # Update inventory
    item.current_stock = new_stock
    
    item.last_updated = datetime.now(timezone.utc)

    db.get(
        Product,
        product_id,
    ).stock_quantity = new_stock

    db.commit()
    db.refresh(item)

    queue_low_stock_emails(
        db,
        background_tasks,
        product_id,
    )

    return item


@router.post("/{product_id}/add-stock", response_model=InventoryResponse)
def add_stock(
    product_id: int,
    data: StockChange,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    result = _change(
    product_id,
    data.quantity,
    True,
    db,
    background_tasks,
)

    queue_low_stock_emails(
        db,
        background_tasks,
        product_id,
    )

    return result


@router.post("/{product_id}/remove-stock", response_model=InventoryResponse)
def remove_stock(
    product_id: int,
    data: StockChange,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF)),
):
    result = _change(
    product_id,
    data.quantity,
    False,
    db,
    background_tasks,
)

    queue_low_stock_emails(
        db,
        background_tasks,
        product_id,
    )

    return result
