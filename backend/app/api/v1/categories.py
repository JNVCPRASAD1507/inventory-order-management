from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.category import Category
from app.models.user import UserRole
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN))):
    if db.scalar(select(Category).where(Category.name.ilike(data.name))):
        raise HTTPException(409, "Duplicate category name")
    item = Category(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.get("", response_model=list[CategoryResponse])
def list_categories(search: str | None = Query(None), skip: int = 0, limit: int = Query(20, le=100), db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF, UserRole.CUSTOMER))):
    stmt = select(Category)
    if search:
        stmt = stmt.where(or_(Category.name.ilike(f"%{search}%"), Category.description.ilike(f"%{search}%")))
    return list(db.scalars(stmt.order_by(Category.id.desc()).offset(skip).limit(limit)))


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN, UserRole.STAFF, UserRole.CUSTOMER))):
    item = db.get(Category, category_id)
    if not item: raise HTTPException(404, "Category not found")
    return item


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN))):
    item = db.get(Category, category_id)
    if not item: raise HTTPException(404, "Category not found")
    duplicate = db.scalar(select(Category).where(Category.name.ilike(data.name), Category.id != category_id))
    if duplicate: raise HTTPException(409, "Duplicate category name")
    for k, v in data.model_dump().items(): setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.ADMIN))):
    item = db.get(Category, category_id)
    if not item: raise HTTPException(404, "Category not found")
    if item.products:
        raise HTTPException(409, "Category cannot be deleted while products use it")
    db.delete(item); db.commit()
    return {"message": "Category deleted"}
