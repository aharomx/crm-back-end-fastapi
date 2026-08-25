from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# Esquema de seguridad para Bearer tokens
security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
) -> User:
    """ 
        Obiene el usuario actual a partir del token JWT.
        Esta dependencia se usa para proteger endpoints.

        Raises:
            HTTPException: Si el token es inválido o el usuario no existe
    """

    token = credentials.credentials

    # Decodificar el token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener email del token
    email: str = payload.get("sub")
    if not email: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar usuario en base de datos
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user

async def get_current_active_superuser(
        current_user: User = Depends(get_current_user)
) -> User:
    """ 
      Verifica que el usuario sea superusuario.
      Útil para endpoints administrativos. 
     
       Raises:
        HTTPException: Si el usuario no es superusuario 
    """

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return current_user


async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """ 
        Retorna el email del usuario autenticado sin consultar la DB.
        Útil cuando solo necesitas el ID de operaciones rápidas.

        Raises:
        HTTPException: Si el token es inválido
    """
    token = credentials.credentials
    payload = decode_token(token)
    if not payload: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return email

async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:

    """ 
         Obtiene el usuario actual si está autenticado, pero no lanza error is no lo está.
         Útil para endpoints que pueden funcionar con o sin autenticación
    """

    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)
    if not payload: 
        return None

    email = payload.get("sub")
    if not email:
        return None

    # Aquí necesitarías acceso a la DB, pero este es un ejemplo
    # Para usar esto, necesitarías inyectar la sesión también
    # Por simplicidad, mejor usa get_current_user directamente

    return None

# Dependencia para verificar que el usuario es el propietario del recurso
async def verify_ownership(
        resource_owner_id: int,
        current_user: User = Depends(get_current_user)
) -> bool:

    """ 
        Verifica que el usuario actual sea el propietario del recurso.
        Útil para endpoints que manejan recursos de usuarios específicos.

        Args:
            resource_owner_id: ID del usuario propietario del recurso
            current_user: Usuario autenticado

        Returns:
            bool: True si es el propietario o superusuario
        
        Raises:
            HTTPException: Si no es el propietario y no es superusuario
    """
    if current_user.id != resource_owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
    return True


# Dependencias por paginación
async def get_pagination_params(
        skip: int = 0,
        limit: int = 100,
) -> dict:

    """ 
        Dependencia para estandarizar los parámetros de paginación
    """
    return {"skip": skip, "limit": limit}