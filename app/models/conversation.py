"""
Conversation Model

Her conversation'ın metadata'sını saklar.
Mesajlar LangGraph state'inde tutulur.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Conversation(Base):
    """Conversation metadata model."""
    
    __tablename__ = "conversations"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations"
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id='{self.id}', title='{self.title}')>"

