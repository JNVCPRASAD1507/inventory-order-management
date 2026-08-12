from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import (
    ChangePasswordRequest, LoginRequest, RegisterRequest, TokenResponse,
    UpdateProfileRequest, UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(409, "Email is already registered")
    user = User(
        full_name=data.full_name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "User is inactive")
    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        user_id=user.id,
        role=user.role,
    )


@router.get("/profile", response_model=UserResponse)
def profile(user: User = Depends(get_current_user)):
    return user


@router.put("/profile", response_model=UserResponse)
def update_profile(data: UpdateProfileRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.full_name = data.full_name
    db.commit()
    db.refresh(user)
    return user


@router.put("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
