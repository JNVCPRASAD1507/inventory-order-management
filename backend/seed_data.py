"""Seed demo users, categories, products for development / first run."""
from app.db.session import SessionLocal, engine, Base
from app.models import *  # noqa
from app.models.user import User, UserRole
from app.models.category import Category, CategoryStatus
from app.models.product import Product, ProductStatus
from app.models.inventory import Inventory
from app.core.security import hash_password
from decimal import Decimal


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Users
        users = [
            ("System Admin", "admin@example.com", "admin123", UserRole.ADMIN),
            ("Staff Member", "staff@example.com", "staff123", UserRole.STAFF),
            ("John Customer", "customer@example.com", "customer123", UserRole.CUSTOMER),
        ]
        for name, email, pwd, role in users:
            if not db.query(User).filter(User.email == email).first():
                db.add(User(
                    full_name=name,
                    email=email,
                    password_hash=hash_password(pwd),
                    role=role,
                    is_active=True,
                ))
        db.commit()

        cats = [
            ("Electronics", "Gadgets and devices"),
            ("Clothing", "Apparel and fashion"),
            ("Books", "Books and literature"),
            ("Home & Kitchen", "Home appliances"),
            ("Sports", "Sports equipment"),
        ]
        for name, desc in cats:
            if not db.query(Category).filter(Category.name == name).first():
                db.add(Category(name=name, description=desc, status=CategoryStatus.ACTIVE))
        db.commit()

        products = [
            ("Wireless Headphones", "Noise-cancelling headphones", 1, "2999.00", "ELEC-HP-001", 50),
            ("Smart Watch", "Fitness smartwatch", 1, "4999.00", "ELEC-SW-002", 30),
            ("Cotton T-Shirt", "Comfortable cotton tee", 2, "599.00", "CLTH-TS-001", 100),
            ("Denim Jeans", "Classic blue jeans", 2, "1499.00", "CLTH-JN-002", 40),
            ("Python Programming", "Learn Python", 3, "799.00", "BOOK-PY-001", 25),
            ("Coffee Maker", "Drip coffee maker", 4, "2499.00", "HOME-CM-001", 15),
            ("Yoga Mat", "Non-slip yoga mat", 5, "899.00", "SPRT-YM-001", 60),
            ("Running Shoes", "Lightweight runners", 5, "3499.00", "SPRT-RS-002", 35),
        ]
        for name, desc, cat_id, price, sku, stock in products:
            if not db.query(Product).filter(Product.sku == sku).first():
                p = Product(
                    name=name,
                    description=desc,
                    category_id=cat_id,
                    price=Decimal(price),
                    sku=sku,
                    stock_quantity=stock,
                    status=ProductStatus.ACTIVE,
                )
                db.add(p)
                db.flush()
                db.add(Inventory(
                    product_id=p.id,
                    current_stock=stock,
                    minimum_stock_level=10,
                    maximum_stock_level=500,
                ))
        db.commit()
        print("Seed OK")
        print("  admin@example.com / admin123")
        print("  staff@example.com / staff123")
        print("  customer@example.com / customer123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
