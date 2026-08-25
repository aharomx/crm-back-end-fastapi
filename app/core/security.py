from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


# Contexto para hashing de contraseñas
pwd_context = CryptContext(
    schemes=["argon2"], 
    deprecated="auto",
    # Configuración para desarrollo (valores más bajos para velocidad)
    argon2__memory_cost=1024, # Memoria en KB (recomendado: 1024-4096)
    argon2__time_cost=2,      # Número de iteraciones (recomendado: 1-4)
    argon2__parallelism=1,     # Hilos de paralelismo (recomndado: 1-4)
    argon2__salt_len=16,       # Longitud de la sal en bytes
    argon2__hash_len=32,       # Longitud del hash en bytes
    )

def verify_password(plain_password:str, hashed_password:str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con el hash
    Estamos usando Argon2 (más seguro que bcrypt)

    Args:
        plain_password (str): _description_
        hashed_password (str): _description_

    Returns:
        bool: _description_
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str)  -> str:
    """
    Genera el  hash de la contraseña usando Argon2
    Argon2 no tiene límite de 72 bytes como bcrypt

    Args:
        password (str): _description_

    Returns:
        str: _description_
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un Token JWT de acceso

    Args:
        data (dict): _description_
        expires_delta (Optional[timedelta], optional): _description_. Defaults to None.

    Returns:
        str: _description_
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow()+expires_delta
    else:
        expire = datetime.utcnow()+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp":expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encode_jwt

def create_refresh_token(data:dict) -> str:
    """
    Crea un toke JWT de refresco para mayor duración

    Args:
        data (dict): _description_

    Returns:
        str: _description_
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type":"refresh"})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encode_jwt


def decode_token(token:str) -> dict:
    """
    Decodifica y valida un token JWT

    Args:
        token (str): _description_

    Returns:
        dict: _description_
    """

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return {}