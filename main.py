from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base

# Importar modelos para que se registren en Base.metadata
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.contacto import Contacto
from app.models.producto import Producto

# Importar router directamente (NO desde app.api)
from app.api.usuarios import router as usuarios_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para CRM de Control de Ventas",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Inicializar base de datos al arrancar"""
    Base.metadata.create_all(bind=engine)
    print("🚀 CRM API iniciado")

# Incluir routers directamente
app.include_router(usuarios_router, prefix="/api/v1/usuarios", tags=["Usuarios"])

@app.get("/")
def root():
    return {
        "message": "CRM API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operativo"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}