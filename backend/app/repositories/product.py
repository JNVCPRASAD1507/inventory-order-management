from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models.product import Product, ProductStatus


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int, for_update: bool = False):
        stmt = select(Product).where(Product.id == product_id)
        if for_update:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list(self, skip: int, limit: int, search=None, category_id=None, min_price=None, max_price=None, status=None):
        stmt = select(Product)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
        if status:
            stmt = stmt.where(Product.status == status)
        return list(self.db.scalars(stmt.order_by(Product.id.desc()).offset(skip).limit(limit)))
