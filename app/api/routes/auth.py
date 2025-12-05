"""
Authentication Routes

Auth ile ilgili HTTP endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.core.exceptions import AlreadyExistsException, UnauthorizedException


router = APIRouter()


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserOut:
    """Yeni kullanıcı kaydı."""
    user_repo = UserRepository(db)
    
    # Email kontrolü
    if await user_repo.exists_by_email(user_data.email):
        raise AlreadyExistsException("User", "email", user_data.email)
    
    # Yeni kullanıcı oluştur
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    
    created_user = await user_repo.create(new_user)
    return created_user


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Login and get access token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Giriş yap ve token al."""
    user_repo = UserRepository(db)
    
    # Kullanıcıyı bul
    user = await user_repo.get_by_email(form_data.username)
    
    # Şifre kontrolü
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedException("Incorrect email or password")
    
    if not user.is_active:
        raise UnauthorizedException("Inactive user")
    
    # Token üret - user.id kullan (email değil)
    access_token = create_access_token(subject=user.id)
    
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Get current authenticated user info"
)
async def get_me(
    db: AsyncSession = Depends(get_db),
    # Not: Bu endpoint için get_current_user dependency'si kullanılacak
    # Ama circular import sorununu önlemek için basit tutuyoruz
) -> UserOut:
    """Mevcut kullanıcı bilgilerini getir."""
    # Bu endpoint'i kullanmak için frontend token gönderecek
    # ve get_current_user dependency'si ile user alınacak
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use /api/v1/users/me endpoint instead"
    )

