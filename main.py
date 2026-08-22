from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.db.init_db import init_db

# Crear la aplicación de FastAPI
app = FastAPI(
     title=settings.PROJECT_NAME,
     description="Api para CRM de control de ventas",
     version="1.0.0",
     docs_url="/docs",
     redoc_url="/redoc"
)

# Configurar CORS (para que el frontend pueda comunicarse)

app.add_middleware(
     CORSMiddleware,
     allow_origins=["htto://localhost:3000"], # Frontend de reflex
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)

# Evento al inicio
@app.on_event("startup")
def on_startup():
     """ Se ejecuta cuando la API inicia"""
     print("🚀 Iniciando CRM API")

     # Crear tablas automáticamente
     Base.metadata.create_all(bind=engine)
     print("✅ Base de datos verificados")


@app.get("/")
def root():
     """ Endpoint raíz"""
     return {
          "message": "CRM API",
          "version": "1.0.0",
          "docs": "/docs",
          "status": "operativo"
     }

@app.get("/healt")
def healt_check():
     """ Endpoint de salud"""
     return {"status": "healthy"}


if __name__ == "__main__":
     import uvicorn
     uvicorn.run(
          "main:app",
          host="0.0.0.0",
          port=8000,
          reload=True,
     )