import secrets
from datetime import datetime, timedelta, timezone
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Form, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.email_service import send_otp_email , send_password_reset_email
from app.models.password_reset import PasswordReset

from app.core.deps import get_current_user, get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.db.session import SessionLocal

from app.models.user import User
from app.models.email_verifications import EmailVerification

from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    SendOTPRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = data.email.lower()

    # Check whether user already exists
    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    # Generate 6-digit OTP
    verification_code = str(secrets.randbelow(900000) + 100000)

    # OTP expires after 5 minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # Create user
    user = User(
        full_name=data.full_name,
        email=email,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
        email_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create email verification record
    verification = EmailVerification(
        email=email,
        otp=verification_code,
        expires_at=expires_at,
        is_verified=False,
    )

    db.add(verification)
    db.commit()

    # Send OTP email
    await send_otp_email(
        email=email,
        name=data.full_name,
        otp=verification_code,
    )

    return user


# ============================================================
# VERIFY EMAIL
# ============================================================


@router.post("/verify-email")
def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    email = data.email.lower()

    # Find user
    user = db.scalar(select(User).where(User.email == email))

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Already verified
    if user.email_verified:
        return {"message": "Email is already verified"}

    # Get latest OTP for this email
    verification = db.scalar(
        select(EmailVerification)
        .where(EmailVerification.email == email)
        .order_by(EmailVerification.id.desc())
    )

    if not verification:
        raise HTTPException(
            status_code=400,
            detail="No verification code found. Please request a new OTP.",
        )

    # Check whether OTP was already used
    if verification.is_verified:
        raise HTTPException(
            status_code=400,
            detail="This verification code has already been used.",
        )

    # Check OTP
    if verification.otp != data.code:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code",
        )

    # Check expiration
    now = datetime.now(timezone.utc)

    if now > verification.expires_at:
        raise HTTPException(
            status_code=400,
            detail="Verification code has expired. Please request a new OTP.",
        )

    # Mark verification as completed
    verification.is_verified = True

    # Mark user's email as verified
    user.email_verified = True

    db.commit()

    return {"message": "Email verified successfully"}


# ============================================================
# SEND / RESEND OTP
# ============================================================


@router.post("/send-otp")
async def send_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db),
):
    email = request.email.lower()

    # Find user
    user = db.scalar(select(User).where(User.email == email))

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Already verified
    if user.email_verified:
        return {"message": "Email is already verified"}

    # Generate new OTP
    otp = str(secrets.randbelow(900000) + 100000)

    # New OTP expires after 5 minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # Create new verification record
    verification = EmailVerification(
        email=email,
        otp=otp,
        expires_at=expires_at,
        is_verified=False,
    )

    db.add(verification)
    db.commit()

    # Send email
    await send_otp_email(
        email=email,
        name=user.full_name,
        otp=otp,
    )

    return {"message": "OTP sent successfully"}


# ============================================================
# LOGIN
# ============================================================


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == data.email.lower()))

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Email verification check
    if not user.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in",
        )

    # Active user check
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive",
        )

    return TokenResponse(
        access_token=create_access_token(
            str(user.id),
            user.role.value,
        ),
        user_id=user.id,
        role=user.role,
    )


@router.post("/token")
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    db = SessionLocal()

    try:
        # OAuth2 username field contains the user's email
        user = db.scalar(
            select(User).where(
                User.email == form_data.username.lower()
            )
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not verify_password(
            form_data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        # OAuth2-compatible JWT
        access_token = create_access_token(
            str(user.id),
            user.role.value,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    finally:
        db.close()
        
        
        
# ============================================================
# PROFILE
# ============================================================


@router.get(
    "/profile",
    response_model=UserResponse,
)
def profile(
    user: User = Depends(get_current_user),
):
    return user


# ============================================================
# UPDATE PROFILE
# ============================================================


@router.put(
    "/profile",
    response_model=UserResponse,
)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.full_name = data.full_name

    db.commit()
    db.refresh(user)

    return user


# ============================================================
# CHANGE PASSWORD
# ============================================================


@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(
        data.current_password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    user.password_hash = hash_password(data.new_password)

    db.commit()

    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    email = data.email.lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Don't reveal whether the email exists.
    if not user:
        return {
            "message": "If the email exists, a password reset link has been sent."
        }

    if not user.is_active:
        return {
            "message": "If the email exists, a password reset link has been sent."
        }

    # Generate secure token
    raw_token = secrets.token_urlsafe(32)

    # Hash token before storing it
    token_hash = hashlib.sha256(
        raw_token.encode()
    ).hexdigest()

    # Token valid for 15 minutes
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=15)
    )

    reset = PasswordReset(
        email=email,
        token_hash=token_hash,
        expires_at=expires_at,
        is_used=False,
    )

    db.add(reset)
    db.commit()

    # Frontend URL
    reset_link = (
        f"http://localhost:5173/reset-password"
        f"?token={raw_token}"
    )

    await send_password_reset_email(
        email=user.email,
        name=user.full_name,
        reset_link=reset_link,
    )

    return {
        "message": "If the email exists, a password reset link has been sent."
    }
    
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    token_hash = hashlib.sha256(
        data.token.encode()
    ).hexdigest()

    reset = db.scalar(
        select(PasswordReset)
        .where(
            PasswordReset.token_hash == token_hash
        )
        .order_by(
            PasswordReset.id.desc()
        )
    )

    if not reset:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    if reset.is_used:
        raise HTTPException(
            status_code=400,
            detail="Reset token has already been used",
        )

    now = datetime.now(timezone.utc)

    if now > reset.expires_at:
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired",
        )

    user = db.scalar(
        select(User).where(
            User.email == reset.email
        )
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Update password
    user.password_hash = hash_password(
        data.new_password
    )

    # Mark token as used
    reset.is_used = True

    db.commit()

    return {
        "message": "Password reset successfully"
    }
