"""
Chat API Routes

Chat ile ilgili HTTP endpoint'leri.
"""

from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    ConversationListResponse,
    MessageSchema
)


router = APIRouter()


# Type aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_chat_service(db: DbSession) -> ChatService:
    """ChatService dependency."""
    return ChatService(db=db)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


@router.post(
    "",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Send a message and receive AI response"
)
async def send_message(
    request: ChatMessageRequest,
    current_user: CurrentUser,
    chat_service: ChatServiceDep
) -> ChatMessageResponse:
    """Mesaj gönder ve cevap al."""
    return await chat_service.send_message(
        user_id=current_user.id,
        message=request.message,
        conversation_id=request.conversation_id
    )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List conversations",
    description="List all conversations for current user"
)
async def list_conversations(
    current_user: CurrentUser,
    chat_service: ChatServiceDep,
    limit: int = 20,
    offset: int = 0
) -> ConversationListResponse:
    """Kullanıcının conversation'larını listele."""
    conversations = await chat_service.list_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations)
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ChatHistoryResponse,
    summary="Get conversation history",
    description="Get message history for a specific conversation"
)
async def get_conversation_history(
    conversation_id: str,
    current_user: CurrentUser,
    chat_service: ChatServiceDep,
    limit: int = 50,
    offset: int = 0
) -> ChatHistoryResponse:
    """Conversation geçmişini getir."""
    messages = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return ChatHistoryResponse(
        conversation_id=conversation_id,
        messages=messages,
        has_more=len(messages) == limit
    )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete conversation",
    description="Delete a conversation and all its messages"
)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    chat_service: ChatServiceDep
) -> None:
    """Conversation sil."""
    await chat_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )

