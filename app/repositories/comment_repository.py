"""
Conversation Repository

Database operations for Comment model.
"""

from typing import Optional, List
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.repositories.base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    """Comment database operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Comment)

    async def count_all(
        self,
        company: Optional[str] = None, 
        category: Optional[str] = None, 
        sentiment_result: Optional[str] = None
    ) -> int:
        """Tüm comment'lerin sayısını getir."""
        query = select(func.count()).select_from(Comment)
        if company:
            query = query.where(Comment.company == company)
        if category:
            query = query.where(Comment.category == category)
        if sentiment_result:
            query = query.where(Comment.sentiment_result == sentiment_result)
        result = await self.db.execute(query)
        return result.scalar_one() or 0

    async def list_all(
        self,
        company: Optional[str] = None, 
        category: Optional[str] = None, 
        sentiment_result: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Comment]:
        """Tüm comment'leri listele."""
        query = select(Comment)
        if company:
            query = query.where(Comment.company == company)
        if category:
            query = query.where(Comment.category == category)
        if sentiment_result:
            query = query.where(Comment.sentiment_result == sentiment_result)
        query = query.order_by(desc(Comment.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())