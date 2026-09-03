"""
LEVELLY — Coach Conversation Model
Records all Levelly Coach interactions
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class CoachConversation(Base):
    __tablename__ = "coach_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    coach_response = Column(Text, nullable=False)
    context_snapshot = Column(JSON, default=dict)  # financial context at time of conversation
    model_used = Column(String(100), nullable=True)  # internal — never shown in UI
    response_source = Column(String(50), default="ai")  # ai or fallback
    session_id = Column(String(100), nullable=True)  # group messages in a session

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="coach_conversations")

    def __repr__(self):
        return f"<CoachConversation id={self.id} user_id={self.user_id}>"
