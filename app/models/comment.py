"""
Comment Model

Kullanıcı yorumları için model.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import String, DateTime, func, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SentimentType(PyEnum):
    """Sentiment değerleri."""
    POSITIVE = "Olumlu"
    NEGATIVE = "Olumsuz"

class Comment(Base):
    """Comment model."""
    
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    
    product_category: Mapped[str] = mapped_column(String(255), nullable=False)
    
    sentiment_result: Mapped[SentimentType] = mapped_column(
        Enum(SentimentType, native_enum=False, length=50),
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, company='{self.company}')>"