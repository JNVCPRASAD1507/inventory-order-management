from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse
from pydantic import BaseModel


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# GET ALL USERS
# Admin only
# ============================================================
class UserStatusUpdate(BaseModel):
    is_active: bool
    


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    users = db.scalars(
        select(User)
        .order_by(User.id.desc())
    ).all()

    return list(users)


# ============================================================
# GET CUSTOMERS
# Admin only
# ============================================================

@router.get(
    "/customers",
    response_model=list[UserResponse],
)
def get_customers(
    db: Session = Depends(get_db),
    admin: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    customers = db.scalars(
        select(User)
        .where(User.role == UserRole.CUSTOMER)
        .order_by(User.id.desc())
    ).all()

    return list(customers)


# ============================================================
# GET STAFF
# Admin only
# ============================================================

@router.get(
    "/staff",
    response_model=list[UserResponse],
)
def get_staff(
    db: Session = Depends(get_db),
    admin: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    staff = db.scalars(
        select(User)
        .where(User.role == UserRole.STAFF)
        .order_by(User.id.desc())
    ).all()

    return list(staff)

@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
)
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Prevent admin from disabling themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own account status",
        )

    # Prevent changing another admin
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be changed here",
        )

    user.is_active = data.is_active

    db.commit()
    db.refresh(user)

    return user
