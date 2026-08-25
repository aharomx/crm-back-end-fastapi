from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token
)


class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data:UserCreate) -> User:
        """
        Registra un nuevo Usuario

        Args:
            db (AsyncSession): _description_
            user_data (UserCreate): _description_

        Returns:
            User: _description_
        """

        # Verificar si el email existe
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Verificar el username existe
        existing_username = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing_username.scalar_one_or_none():
            raise ValueError("Username already taken")

        # Crear nuevo usuario
        db_user = User(
            email=user_data.email,
            username= user_data.username,
            full_name= user_data.full_name,
            hashed_password = get_password_hash(user_data.password)
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user


    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password:str) -> Optional[User]:
        """
        Autentica un usuario por email y contraseña

        Args:
            db (AsyncSession): _description_
            email (str): _description_
            password (str): _description_

        Returns:
            Optional[User]: _description_
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None

        return user

    @staticmethod
    def create_token(user:User) -> dict:
        """
        Crea tokens de acceso y refresco de para un usuario

        Args:
            user (User): _description_

        Returns:
            dict: _description_
        """

        access_token = create_access_token(
            data={"sub": user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        