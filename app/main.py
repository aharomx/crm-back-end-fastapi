# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, prospects, clients, calls, appointments
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Registrar routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(prospects.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(calls.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "database": settings.DATABASE_URL.split("://")[0]
    }

# Endpoint para debug de OpenAPI
@app.get("/debug/openapi")
async def debug_openapi():
    """Endpoint para debug - muestra el schema OpenAPI"""
    return app.openapi()