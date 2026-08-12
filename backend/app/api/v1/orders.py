from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, require_roles
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order import create_order, transition_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create(data: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    try:
        return create_order(db, user.id, data, background_tasks)
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(500, "Order creation failed")


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Order).options(joinedload(Order.items))
    if user.role == UserRole.CUSTOMER:
        stmt = stmt.where(Order.customer_id == user.id)
    return list(db.scalars(stmt.order_by(Order.id.desc())).unique())


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.scalar(select(Order).options(joinedload(Order.items)).where(Order.id == order_id))
    if not order: raise HTTPException(404, "Order not found")
    if user.role == UserRole.CUSTOMER and order.customer_id != user.id:
        raise HTTPException(403, "Not allowed")
    return order


def _transition(order_id, target, background_tasks, db, user):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Order not found")
    return transition_order(db, order, target, background_tasks)


@router.put("/{order_id}/confirm", response_model=OrderResponse)
def confirm(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    return _transition(order_id, OrderStatus.CONFIRMED, background_tasks, db, _)


@router.put("/{order_id}/ship", response_model=OrderResponse)
def ship(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    return _transition(order_id, OrderStatus.SHIPPED, background_tasks, db, _)


@router.put("/{order_id}/deliver", response_model=OrderResponse)
def deliver(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    return _transition(order_id, OrderStatus.DELIVERED, background_tasks, db, _)


@router.put("/{order_id}/cancel", response_model=OrderResponse)
def cancel(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Order not found")
    if user.role == UserRole.CUSTOMER and order.customer_id != user.id:
        raise HTTPException(403, "Not allowed")
    return transition_order(db, order, OrderStatus.CANCELLED, background_tasks)
