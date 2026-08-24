# app/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Configuración del engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,  # Log de SQL (útil para depurar)
    future=True,  # Usa la nueva sintaxis de SQLAlchemy 2.0
)

# Fábrica de sesiones async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Los objetos no expiran después del commit
)

# Base para modelos
Base = declarative_base()

# Dependencia para obtener sesión en endpoints
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()