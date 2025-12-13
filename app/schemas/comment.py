"""
Comment Schemas

Pydantic models for comment API validation and serialization.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment type for API."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class CommentCreate(BaseModel):
    """Comment creation request."""
    content: str = Field(..., min_length=1, max_length=10000)
    company: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=255)
    product_category: str = Field(..., min_length=1, max_length=255)
    sentiment_result: SentimentType


class CommentUpdate(BaseModel):
    """Comment update request."""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=255)
    product_category: Optional[str] = Field(None, min_length=1, max_length=255)
    sentiment_result: Optional[SentimentType] = None


class CommentResponse(BaseModel):
    """Comment response."""
    id: int
    content: str
    company: str
    category: str
    product_category: str
    sentiment_result: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    """Comment list response."""
    comments: List[CommentResponse]
    total: int
