"""
Chat Schemas

Pydantic models for chat API validation and serialization.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Chat mesajı gönderme request'i."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message content"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID. If null, creates new conversation."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Python nedir?",
                "conversation_id": None
            }
        }


class MessageSchema(BaseModel):
    """Tek bir mesajı temsil eder."""
    role: Literal["human", "assistant"] = Field(
        ...,
        description="Message sender role"
    )
    content: str = Field(
        ...,
        description="Message content"
    )
    timestamp: datetime = Field(
        ...,
        description="Message timestamp"
    )


class ChatMessageResponse(BaseModel):
    """Chat mesajı response'u."""
    response: str = Field(
        ...,
        description="AI response content"
    )
    conversation_id: str = Field(
        ...,
        description="Conversation ID for continuing chat"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Python, yüksek seviyeli bir programlama dilidir...",
                "conversation_id": "abc-123-def-456"
            }
        }


class ConversationSchema(BaseModel):
    """Conversation metadata."""
    id: str
    title: Optional[str]
    created_at: datetime
    last_message_at: datetime
    message_count: int = Field(default=0)
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Conversation listesi response'u."""
    conversations: list[ConversationSchema]
    total: int


class ChatHistoryResponse(BaseModel):
    """Conversation geçmişi response'u."""
    conversation_id: str
    messages: list[MessageSchema]
    has_more: bool = Field(
        default=False,
        description="More messages available for pagination"
    )

