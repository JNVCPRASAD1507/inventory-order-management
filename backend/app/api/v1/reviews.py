from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.models.review import Review
from app.models.user import User, UserRole
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.services.review import average_rating, create_review

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
def create(data: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    return create_review(db, user.id, data)


@router.get("/product/{product_id}")
def list_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = list(db.scalars(select(Review).where(Review.product_id == product_id).order_by(Review.id.desc())))
    return {"average_rating": average_rating(db, product_id), "reviews": [ReviewResponse.model_validate(r) for r in reviews]}


@router.put("/{review_id}", response_model=ReviewResponse)
def update(review_id: int, data: ReviewUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    item = db.get(Review, review_id)
    if not item or item.customer_id != user.id: raise HTTPException(404, "Review not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


@router.delete("/{review_id}")
def delete(review_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    item = db.get(Review, review_id)
    if not item or item.customer_id != user.id: raise HTTPException(404, "Review not found")
    db.delete(item); db.commit()
    return {"message": "Review deleted"}
