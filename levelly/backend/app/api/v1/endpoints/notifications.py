"""
LEVELLY — Notifications Endpoints
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()


@router.get("/")
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 30,
    unread_only: bool = False,
):
    """Get notifications for current user."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "priority": n.priority,
            "is_read": n.is_read,
            "action_url": n.action_url,
            "created_at": n.created_at.isoformat(),
            "read_at": n.read_at.isoformat() if n.read_at else None,
        }
        for n in notifications
    ]


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get count of unread notifications."""
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .count()
    )
    return {"unread_count": count}


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if notification:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
    return {"success": True}


@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Mark all notifications as read."""
    now = datetime.now(timezone.utc)
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True, "read_at": now})
    db.commit()
    return {"success": True}
