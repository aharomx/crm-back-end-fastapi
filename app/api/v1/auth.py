from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a mew user

    Args:
        user_data (UserCreate): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
    """
    try:
        user = await AuthService.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login de usuario - retorna tokens jwt

    Args:
        user_data (UserLogin): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
    """

    user = await AuthService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrect",
            headers={"WWW-Authenticate":"Bearer"}
        )

    tokens = AuthService.create_token(user)
    return tokens



@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using the refresh token

    Args:
        refresh_token (str): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
    """

    from app.core.security import decode_token

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Verify if user still exist
    from sqlalchemy import select
    from app.models.user import User

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    tokens = AuthService.create_token(user)
    return tokens
