from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.id.desc()).limit(100)))


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Notification, notification_id)
    if not item or item.user_id != user.id: raise HTTPException(404, "Notification not found")
    item.is_read = True
    db.commit(); db.refresh(item)
    return item
