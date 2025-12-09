"""
Comments API Routes

Comments ile ilgili HTTP endpoint'leri.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.comment import CommentCreate, CommentUpdate, CommentListResponse,CommentResponse, ModelSentimentType
from app.repositories.comment_repository import CommentRepository
from app.models.comment import Comment

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]

def get_comment_repository(db: DbSession) -> CommentRepository:
    """CommentRepository dependency."""
    return CommentRepository(db=db)

CommentRepositoryDep = Annotated[CommentRepository, Depends(CommentRepository)]

@router.post("", 
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new comment",
    description="Create a new comment for a company"
)
async def create_comment(
    comment: CommentCreate,
    repo: CommentRepositoryDep,
) -> CommentResponse:
    """Yeni comment oluştur."""
    comment = Comment(
        content=comment.content,
        company=comment.company,
        category=comment.category,
        sentiment_result= ModelSentimentType
    )
    created_comment = await repo.create(comment)
    return CommentResponse.model_validate(created_comment)

@router.get("",
    response_model=CommentListResponse,
    summary="Get all comments",
    description="Get all comments for a company"
)
async def get_all_comments(
    repo: CommentRepositoryDep,
    limit: int = 50,
    offset: int = 0,
    company: Optional[str] = None,
    category: Optional[str] = None,
    sentiment_result: Optional[ModelSentimentType] = None,
) -> CommentListResponse:
    """Tüm comment'leri getir."""

    model_sentiment_result = ModelSentimentType(sentiment_result).value if sentiment_result else None
    comments = await repo.list_all(
        company=company,
        category=category,
        sentiment_result=model_sentiment_result
    )
    total = await repo.count_all(
        company=company,
        category=category,
        sentiment_result=model_sentiment_result
    )
    return CommentListResponse.model_validate(comments, total=total)

@router.get("/{comment_id}",
    response_model=CommentResponse,
    summary="Get a comment by id",
    description="Get a comment by id"
)
async def get_comment_by_id(
    comment_id: int,
    repo: CommentRepositoryDep,
) -> CommentResponse:
    """ID ile comment getir."""
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return CommentResponse.model_validate(comment)

@router.put("/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment by id",
    description="Update a comment by id"
)
async def update_comment_by_id(
    comment_id: int,
    comment_data: CommentUpdate,
    repo: CommentRepositoryDep,
) -> CommentResponse:
    """ID ile comment güncelle."""
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Comment not found")
    comment.content = comment_data.content if comment_data.content else comment.content
    comment.company = comment_data.company if comment_data.company else comment.company
    comment.category = comment_data.category if comment_data.category else comment.category
    comment.sentiment_result = comment_data.sentiment_result if comment_data.sentiment_result else comment.sentiment_result
    updated_comment = await repo.update(comment)
    return CommentResponse.model_validate(updated_comment)

@router.delete("/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment by id",
    description="Delete a comment by id"
)
async def delete_comment_by_id(
    comment_id: int,
    repo: CommentRepositoryDep,
) -> None:
    """ID ile comment sil."""
    comment = await repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Comment not found")
    await repo.delete(comment)