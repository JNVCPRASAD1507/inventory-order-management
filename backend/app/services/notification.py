from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType


def create_notification(db: Session, user_id: int, title: str, message: str, notification_type: NotificationType):
    db.add(Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
    ))


def queue_notification(background_tasks, user_id: int, title: str, message: str, notification_type: NotificationType):
    # BackgroundTasks receives serializable values; DB work is performed in a fresh session.
    from app.db.session import SessionLocal

    def task():
        db = SessionLocal()
        try:
            create_notification(db, user_id, title, message, notification_type)
            db.commit()
        finally:
            db.close()

    background_tasks.add_task(task)
