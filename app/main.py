# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

@app.on_event("startup")
async def startup():
    """Crear tablas al iniciar (solo para desarrollo)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API funciona"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "database": settings.DATABASE_URL.split("://")[0]  # Muestra el tipo de DB
    }