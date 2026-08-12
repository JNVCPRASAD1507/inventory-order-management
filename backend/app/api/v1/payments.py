from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.models.payment import Payment
from app.models.user import User, UserRole
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment import create_payment, refund_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=201)
def create(data: PaymentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    return create_payment(db, user.id, data.order_id, data.payment_method, background_tasks)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get(payment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    payment = db.get(Payment, payment_id)
    if not payment: raise HTTPException(404, "Payment not found")
    if user.role == UserRole.CUSTOMER and payment.order.customer_id != user.id:
        raise HTTPException(403, "Not allowed")
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund(payment_id: int, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    payment = db.get(Payment, payment_id)
    if not payment: raise HTTPException(404, "Payment not found")
    return refund_payment(db, payment)
