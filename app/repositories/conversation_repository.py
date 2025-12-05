"""
Conversation Repository

Database operations for Conversation model.
"""

from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Conversation database operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Conversation)
    
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """ID ile conversation getir."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_user(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> list[Conversation]:
        """Kullanıcının conversation'larını listele."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.last_message_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: int) -> int:
        """Kullanıcının conversation sayısını getir."""
        result = await self.db.execute(
            select(Conversation.id)
            .where(Conversation.user_id == user_id)
        )
        return len(result.scalars().all())

