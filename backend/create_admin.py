from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


db = SessionLocal()

try:
    existing_admin = db.query(User).filter(
        User.role == UserRole.ADMIN
    ).first()

    if existing_admin:
        print("Admin already exists.")
    else:
        admin = User(
            full_name="System Admin Prasad",
            email="chandraprasadkolli@gmail.com",
            password_hash=hash_password("chandra123"),
            role=UserRole.ADMIN,
            is_active=True,
            email_verified=True,
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

finally:
    db.close()