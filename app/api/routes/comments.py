"""
Comments API Routes

Comments ile ilgili HTTP endpoint'leri.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentListResponse,
    CommentResponse,
    SentimentType
)
from app.repositories.comment_repository import CommentRepository
from app.models.comment import Comment, SentimentType as ModelSentimentType

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_comment_repository(db: DbSession) -> CommentRepository:
    """CommentRepository dependency."""
    return CommentRepository(db=db)


CommentRepoDep = Annotated[CommentRepository, Depends(get_comment_repository)]


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new comment",
    description="Create a new comment for a company"
)
async def create_comment(
    comment_data: CommentCreate,
    repo: CommentRepoDep,
) -> CommentResponse:
    """Yeni comment oluştur."""
    comment = Comment(
        content=comment_data.content,
        company=comment_data.company,
        category=comment_data.category,
        product_category=comment_data.product_category,
        sentiment_result=ModelSentimentType(comment_data.sentiment_result)
    )
    created_comment = await repo.create(comment)
    return CommentResponse.model_validate(created_comment)


@router.get(
    "",
    response_model=CommentListResponse,
    summary="Get all comments",
    description="Get all comments with optional filters"
)
async def get_all_comments(
    repo: CommentRepoDep,
    limit: int = 50,
    offset: int = 0,
    company: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[SentimentType] = None,
) -> CommentListResponse:
    """Tüm comment'leri getir."""
    model_sentiment = ModelSentimentType(sentiment.value) if sentiment else None
    
    comments = await repo.list_all(
        limit=limit,
        offset=offset,
        company=company,
        category=category,
        sentiment_result=model_sentiment
    )
    total = await repo.count_all(
        company=company,
        category=category,
        sentiment_result=model_sentiment
    )
    
    return CommentListResponse(
        comments=[CommentResponse.model_validate(c) for c in comments],
        total=total
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Get a comment by id",
    description="Get a comment by id"
)
async def get_comment_by_id(
    comment_id: int,
    repo: CommentRepoDep,
) -> CommentResponse:
    """ID ile comment getir."""
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return CommentResponse.model_validate(comment)


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment by id",
    description="Update a comment by id"
)
async def update_comment_by_id(
    comment_id: int,
    comment_data: CommentUpdate,
    repo: CommentRepoDep,
) -> CommentResponse:
    """ID ile comment güncelle."""
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment_data.content is not None:
        comment.content = comment_data.content
    if comment_data.company is not None:
        comment.company = comment_data.company
    if comment_data.category is not None:
        comment.category = comment_data.category
    if comment_data.product_category is not None:
        comment.product_category = comment_data.product_category
    if comment_data.sentiment_result is not None:
        comment.sentiment_result = ModelSentimentType(comment_data.sentiment_result.value)
    
    updated_comment = await repo.update(comment)
    return CommentResponse.model_validate(updated_comment)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment by id",
    description="Delete a comment by id"
)
async def delete_comment_by_id(
    comment_id: int,
    repo: CommentRepoDep,
) -> None:
    """ID ile comment sil."""
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    await repo.delete(comment)
