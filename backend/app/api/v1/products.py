from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.core.config import settings
from app.models.product import Product, ProductStatus
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.user import UserRole
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.utils.files import save_upload

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    if not db.get(Category, data.category_id):
        raise HTTPException(404, "Category not found")
    if db.scalar(select(Product).where(Product.sku == data.sku)):
        raise HTTPException(409, "SKU already exists")
    product = Product(**data.model_dump())
    db.add(product); db.flush()
    db.add(Inventory(product_id=product.id, current_stock=data.stock_quantity, minimum_stock_level=5, maximum_stock_level=1000))
    db.commit(); db.refresh(product)
    return product


@router.get("", response_model=list[ProductResponse])
def list_products(
    search: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    status: ProductStatus | None = None,
    skip: int = 0,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF, UserRole.CUSTOMER)),
):
    from app.repositories.product import ProductRepository
    return ProductRepository(db).list(skip, limit, search, category_id, min_price, max_price, status)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF, UserRole.CUSTOMER))):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    return item


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    payload = data.model_dump(exclude_unset=True)
    if "sku" in payload and db.scalar(select(Product).where(Product.sku == payload["sku"], Product.id != product_id)):
        raise HTTPException(409, "SKU already exists")
    for k, v in payload.items(): setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN))):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    item.status = ProductStatus.INACTIVE
    db.commit()
    return {"message": "Product deactivated"}


@router.post("/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF))):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Product not found")
    path = await save_upload(file, user.id, db)
    product.image_path = path
    db.commit(); db.refresh(product)
    return product
