from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings


# crear el motor de la base da datos
# pool_pre_ping=True verifica que la conexión esté viva antes de usarla

engine =create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=True, # Muestra las consultas SQL en consola (util para desarrollo)
)

# Crear la fabrica de sesiones
# Cada sesión es una "conversación" con la base de datos
SessionLocal = sessionmaker(
    autocomit=False,
    autoflush=False,
    bind=engine
)

# Clase base para todos los modelos
Base = declarative_base()

# Función para obtener una sesión de base de datos
def get_db():
    """
     Dependency poara FastAPI que maneja el ciclo de vida de la sesión.
     Se usa en los endpoints para acceder a la base de datos.
    """

    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

    