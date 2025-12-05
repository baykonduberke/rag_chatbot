"""
Chat Service

Chat ile ilgili tüm business logic burada.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.agents.state import AgentState
from app.agents.graph import get_compiled_graph
from app.schemas.chat import (
    ChatMessageResponse,
    ConversationSchema,
    MessageSchema
)
from app.core.exceptions import NotFoundException


class ChatService:
    """Chat service layer."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.graph = get_compiled_graph(with_memory=True)
        self.conversation_repo = ConversationRepository(db)
    
    async def send_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ) -> ChatMessageResponse:
        """Mesaj gönder ve cevap al."""
        
        # Conversation al veya oluştur
        if conversation_id:
            conversation = await self._get_conversation(
                conversation_id, user_id
            )
        else:
            conversation = await self._create_conversation(user_id)
        
        # Initial state hazırla
        initial_state = AgentState(
            messages=[],
            user_id=str(user_id),
            thread_id=conversation.id,
            last_question=message,
            last_answer="",
            context=None,
            error=None
        )
        
        # Config: thread_id ile state izole edilir
        config = {
            "configurable": {
                "thread_id": conversation.id
            }
        }
        
        # Graph invoke et
        result = self.graph.invoke(initial_state, config)
        
        # Conversation metadata güncelle
        await self._update_conversation_timestamp(conversation)
        
        # İlk mesajdan title oluştur
        if not conversation.title:
            conversation.title = message[:50] + ("..." if len(message) > 50 else "")
            await self.conversation_repo.update(conversation)
        
        return ChatMessageResponse(
            response=result["last_answer"],
            conversation_id=conversation.id
        )
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[MessageSchema]:
        """Conversation geçmişini getir."""
        
        # Ownership check
        await self._get_conversation(conversation_id, user_id)
        
        # Graph state'inden mesajları çek
        config = {"configurable": {"thread_id": conversation_id}}
        
        try:
            state = self.graph.get_state(config)
            if not state or not state.values:
                return []
            
            messages = state.values.get("messages", [])
        except Exception:
            return []
        
        # Convert to schema
        result = []
        for msg in messages[offset:offset + limit]:
            role = "human" if msg.type == "human" else "assistant"
            result.append(MessageSchema(
                role=role,
                content=msg.content,
                timestamp=datetime.now()
            ))
        
        return result
    
    async def list_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> list[ConversationSchema]:
        """Kullanıcının conversation'larını listele."""
        
        conversations = await self.conversation_repo.list_by_user(
            user_id, limit, offset
        )
        
        return [
            ConversationSchema(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                last_message_at=c.last_message_at,
                message_count=0
            )
            for c in conversations
        ]
    
    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> None:
        """Conversation sil."""
        conversation = await self._get_conversation(conversation_id, user_id)
        await self.conversation_repo.delete(conversation)
    
    async def _get_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> Conversation:
        """Get conversation with ownership check."""
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        
        if not conversation:
            raise NotFoundException("Conversation", conversation_id)
        
        if conversation.user_id != user_id:
            raise NotFoundException("Conversation", conversation_id)
        
        return conversation
    
    async def _create_conversation(self, user_id: int) -> Conversation:
        """Create new conversation."""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=None
        )
        return await self.conversation_repo.create(conversation)
    
    async def _update_conversation_timestamp(
        self,
        conversation: Conversation
    ) -> None:
        """Update last_message_at timestamp."""
        conversation.last_message_at = datetime.now()
        await self.conversation_repo.update(conversation)

